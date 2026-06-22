"""Application service orchestrating logic extraction for repositories and commits."""

import os
from datetime import datetime
from typing import Callable, Optional
import uuid

from src.application.ports.git_port import IGitAdapter
from src.application.ports.parser_port import IParser
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.entities.logic_transition import LogicTransition
from src.domain.enums.entity_type import EntityType
from src.domain.enums.transition_type import TransitionType
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.entity_id import SEID
from src.infrastructure.logic.behavior_drift_engine import BehaviorDriftEngine
from src.infrastructure.logic.logic_diff_engine import LogicDiffEngine
from src.infrastructure.logic.logic_extraction_engine import LogicExtractionEngine
from src.infrastructure.logic.logic_similarity_engine import LogicSimilarityEngine


class LogicExtractionOrchestrator:
    """Orchestrator that walks repository snapshot entities, runs extraction, and links evolution timelines."""

    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        git_adapter: IGitAdapter,
        parser: IParser,
        extraction_engine: LogicExtractionEngine,
        similarity_engine: LogicSimilarityEngine,
        diff_engine: LogicDiffEngine,
        drift_engine: BehaviorDriftEngine,
    ) -> None:
        self._uow_factory = uow_factory
        self._git_adapter = git_adapter
        self._parser = parser
        self._extraction_engine = extraction_engine
        self._similarity_engine = similarity_engine
        self._diff_engine = diff_engine
        self._drift_engine = drift_engine

    def extract_repository_logic(
        self, repository_id: RepositoryId, commit_hash: str
    ) -> None:
        """
        Run logic extraction for all active code entities at the given commit.

        This checks out the commit, reads files, runs the extraction engine,
        generates signatures/versions/evidence, and computes transitions/drift.
        """
        print(f"[LogicOrchestrator] extract_repository_logic called for repo={repository_id.value}, commit={commit_hash}")
        # 1. Fetch Repository and Checkout commit
        with self._uow_factory() as uow:
            repo = uow.repositories.get_by_id(repository_id)
            if not repo:
                print(f"[LogicOrchestrator] Repository {repository_id.value} not found.")
                return
            local_path = repo.local_path

        self._git_adapter.checkout_commit(local_path, commit_hash)

        # 2. Reconstruct active entities at this commit
        from src.application.services.historical_reconstruction import HistoricalReconstructionService
        reconstructor = HistoricalReconstructionService()
        with self._uow_factory() as uow:
            try:
                active_entities, _ = reconstructor.reconstruct_graph_at_commit(
                    uow, repository_id, commit_hash
                )
            except Exception as e:
                print(f"[LogicOrchestrator] Graph reconstruction failed: {e}. Falling back to snapshot.")
                # Fallback to snapshot if reconstruction fails
                snapshot = uow.snapshots.get_by_commit(repository_id, commit_hash)
                if snapshot:
                    active_entities = []
                    for seid in snapshot.entity_seids:
                        entity = uow.code_entities.get_by_seid(seid)
                        if entity:
                            active_entities.append(entity)
                else:
                    print(f"[LogicOrchestrator] Snapshot fallback also failed/missing.")
                    return

        print(f"[LogicOrchestrator] Reconstructed {len(active_entities)} active entities.")

        # 3. Group active entities by file
        from collections import defaultdict
        file_groups = defaultdict(list)
        for entity in active_entities:
            if entity.entity_type in (EntityType.FUNCTION, EntityType.METHOD):
                file_groups[entity.location.file_path].append(entity)

        # 4. Iterate on a per-file basis
        for file_path, entities_in_file in file_groups.items():
            file_abs_path = os.path.join(local_path, file_path)
            if not os.path.exists(file_abs_path):
                print(f"[LogicOrchestrator] File does not exist: {file_abs_path}")
                continue

            try:
                with open(file_abs_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
            except Exception as e:
                print(f"[LogicOrchestrator] Failed to read file {file_abs_path}: {e}")
                continue

            # Parse the file into a tree-sitter AST once per file
            try:
                parse_result = self._parser.parse_file(
                    file_path, file_content, entities_in_file[0].language
                )
            except Exception as e:
                print(f"[LogicOrchestrator] Parser failed for {file_path}: {e}")
                continue

            # Process all entities of this file under a single transaction block
            with self._uow_factory() as uow:
                for entity in entities_in_file:
                    print(f"[LogicOrchestrator] Entity matches type check: name={entity.qualified_name}, type={entity.entity_type}")

                    # Extract logic items matching patterns
                    try:
                        extracted_items = self._extraction_engine.extract_logic(
                            entity, parse_result.tree, file_content, commit_hash
                        )
                    except Exception as e:
                        print(f"[LogicOrchestrator] Extraction engine failed for {entity.qualified_name}: {e}")
                        continue

                    if extracted_items:
                        print(f"[LogicOrchestrator] Extracted {len(extracted_items)} logic items for {entity.qualified_name}!")

                    for signature, version, evidence_list, explanation in extracted_items:
                        # Associate CodeEntity details to signature metadata for persistence mapping
                        signature.metadata["entity_seid"] = str(entity.seid.value)
                        signature.metadata["entity_name"] = entity.qualified_name
                        signature.metadata["entity_type"] = entity.entity_type.value
                        signature.metadata["file_path"] = entity.location.file_path
                        signature.metadata["overall_confidence"] = version.overall_confidence

                        version.metadata["entity_seid"] = str(entity.seid.value)
                        version.metadata["line_start"] = entity.location.start_line
                        version.metadata["line_end"] = entity.location.end_line

                        # Check if signature exists, and save
                        uow.logic_signatures.save(signature)

                        # Link timeline to previous version
                        prev_versions = uow.logic_versions.list_by_signature(
                            signature.id
                        )

                        # Idempotency check: check if a version for this commit already exists
                        existing_ver = next((v for v in prev_versions if v.commit_hash == commit_hash), None)
                        if existing_ver:
                            # Reuse the version ID
                            version.id = existing_ver.id
                            # Remove existing evidence for this version before saving new evidence
                            uow.logic_evidence.delete_by_logic_version(existing_ver.id)
                            # Filter out the existing version from prev_versions list for timeline linking
                            prev_versions = [v for v in prev_versions if v.id != existing_ver.id]

                        if prev_versions:
                            # Sort chronologically by version number
                            prev_versions.sort(key=lambda x: x.version_ordinal)
                            latest_prev = prev_versions[-1]

                            # Assign ordinal
                            version.version_ordinal = latest_prev.version_ordinal + 1

                            # Compute similarity and diff
                            similarity = self._similarity_engine.compute_version_similarity(
                                latest_prev, version
                            )
                            diff = self._diff_engine.diff_versions(latest_prev, version)

                            # Determine transition type
                            if similarity >= 0.99:
                                trans_type = TransitionType.UNCHANGED
                            elif similarity >= 0.30:
                                trans_type = TransitionType.EVOLVED
                            else:
                                trans_type = TransitionType.REPLACED

                            # Create Transition
                            transition = LogicTransition(
                                id=uuid.uuid4(),
                                from_logic_version_id=latest_prev.id,
                                to_logic_version_id=version.id,
                                transition_type=trans_type,
                                similarity_score=similarity,
                                overall_confidence=version.overall_confidence,
                                metadata={
                                    "from_commit": latest_prev.commit_hash,
                                    "to_commit": version.commit_hash,
                                    "summary": diff.get("summary", ""),
                                    "dependency_hash": version.fingerprint.dependency_hash,
                                    "behavioral_hash": version.fingerprint.behavioral_hash,
                                },
                                created_at=datetime.utcnow(),
                            )

                            # Reuse transition ID if it exists
                            if existing_ver:
                                existing_trans = uow.logic_transitions.get_by_to_version(existing_ver.id)
                                if existing_trans:
                                    transition.id = existing_trans[0].id

                            # Compute behavior drift
                            drift = self._drift_engine.compute_drift(
                                transition, latest_prev, version
                            )

                            # Reuse drift ID if it exists
                            if existing_ver:
                                existing_drift = uow.behavior_drift.get_by_transition(transition.id)
                                if existing_drift:
                                    drift.id = existing_drift.id

                            # Save Transition & Drift
                            uow.logic_transitions.save(transition)
                            uow.behavior_drift.save(drift)
                        else:
                            # First appearance
                            version.version_ordinal = 1
                            transition = LogicTransition(
                                id=uuid.uuid4(),
                                from_logic_version_id=None,
                                to_logic_version_id=version.id,
                                transition_type=TransitionType.CREATED,
                                similarity_score=1.0,
                                overall_confidence=version.overall_confidence,
                                metadata={
                                    "to_commit": version.commit_hash,
                                    "summary": "First appearance of this behavioral logic in codebase.",
                                    "dependency_hash": version.fingerprint.dependency_hash,
                                    "behavioral_hash": version.fingerprint.behavioral_hash,
                                },
                                created_at=datetime.utcnow(),
                            )

                            # Reuse transition ID if it exists
                            if existing_ver:
                                existing_trans = uow.logic_transitions.get_by_to_version(existing_ver.id)
                                if existing_trans:
                                    transition.id = existing_trans[0].id

                            uow.logic_transitions.save(transition)

                        # Reuse explanation ID if it exists
                        if existing_ver:
                            existing_exp = uow.behavior_explanations.get_by_logic_version(existing_ver.id)
                            if existing_exp:
                                explanation.id = existing_exp.id

                        # Save Version, Evidence, and Explanation
                        uow.logic_versions.save(version)
                        uow.logic_evidence.save_batch(evidence_list)
                        uow.behavior_explanations.save(explanation)

                # Commit once per file
                uow.commit()

    def extract_all_repository_logic(self, repository_id: RepositoryId) -> None:
        """
        Run logic extraction chronologically across all commits of the repository,
        applying incremental processing (delta walking) to only checkout and parse
        files containing code entities that were created or modified in each commit.
        """
        print(f"[LogicOrchestrator] extract_all_repository_logic called for repo={repository_id.value}")

        # 1. Fetch Repository
        with self._uow_factory() as uow:
            repo = uow.repositories.get_by_id(repository_id)
            if not repo:
                print(f"[LogicOrchestrator] Repository {repository_id.value} not found.")
                return
            local_path = repo.local_path
            default_branch = repo.default_branch or "main"

        # 2. Get all commits chronologically
        with self._uow_factory() as uow:
            commits = uow.commits.list_by_repository(repository_id)
            # Sort commits chronologically by timestamp
            commits.sort(key=lambda x: x.timestamp)

        if not commits:
            print("[LogicOrchestrator] No commits found for this repository.")
            return

        print(f"[LogicOrchestrator] Found {len(commits)} commits to process.")

        try:
            for idx, commit in enumerate(commits):
                commit_hash = commit.hash
                print(f"[LogicOrchestrator] [{idx+1}/{len(commits)}] Processing commit {commit_hash}")

                # For the very first commit, we must extract logic for all active entities.
                if idx == 0:
                    self.extract_repository_logic(repository_id, commit_hash)
                    continue

                # For subsequent commits, optimize using delta walking:
                # Query the change events in this commit to find which code entities were CREATED, MODIFIED, RENAMED, or MOVED.
                with self._uow_factory() as uow:
                    change_events = uow.change_events.get_by_commit(commit_hash)
                    changed_seids = {
                        e.seid for e in change_events
                        if e.change_type.value in ("CREATED", "MODIFIED", "RENAMED", "MOVED")
                    }

                if not changed_seids:
                    print(f"[LogicOrchestrator] No entities changed in commit {commit_hash}. Skipping extraction.")
                    continue

                print(f"[LogicOrchestrator] {len(changed_seids)} changed entities detected in commit {commit_hash}.")

                # 3. Checkout commit
                self._git_adapter.checkout_commit(local_path, commit_hash)

                # 4. Fetch the specific changed entities from the DB
                with self._uow_factory() as uow:
                    changed_entities = []
                    for seid in changed_seids:
                        entity = uow.code_entities.get_by_seid(seid)
                        if entity and entity.entity_type.value in ("FUNCTION", "METHOD"):
                            changed_entities.append(entity)

                if not changed_entities:
                    print(f"[LogicOrchestrator] No function/method entities changed in commit {commit_hash}.")
                    continue

                # 5. Group entities by file
                from collections import defaultdict
                file_groups = defaultdict(list)
                for entity in changed_entities:
                    file_groups[entity.location.file_path].append(entity)

                # 6. Iterate and extract per file
                for file_path, entities_in_file in file_groups.items():
                    file_abs_path = os.path.join(local_path, file_path)
                    if not os.path.exists(file_abs_path):
                        continue

                    try:
                        with open(file_abs_path, "r", encoding="utf-8") as f:
                            file_content = f.read()
                    except Exception as e:
                        print(f"[LogicOrchestrator] Failed to read {file_abs_path}: {e}")
                        continue

                    try:
                        parse_result = self._parser.parse_file(
                            file_path, file_content, entities_in_file[0].language
                        )
                    except Exception as e:
                        print(f"[LogicOrchestrator] Parser failed for {file_path}: {e}")
                        continue

                    with self._uow_factory() as uow:
                        for entity in entities_in_file:
                            try:
                                extracted_items = self._extraction_engine.extract_logic(
                                    entity, parse_result.tree, file_content, commit_hash
                                )
                            except Exception as e:
                                print(f"[LogicOrchestrator] Extraction engine failed for {entity.qualified_name}: {e}")
                                continue

                            for signature, version, evidence_list, explanation in extracted_items:
                                signature.metadata["entity_seid"] = str(entity.seid.value)
                                signature.metadata["entity_name"] = entity.qualified_name
                                signature.metadata["entity_type"] = entity.entity_type.value
                                signature.metadata["file_path"] = entity.location.file_path
                                signature.metadata["overall_confidence"] = version.overall_confidence

                                version.metadata["entity_seid"] = str(entity.seid.value)
                                version.metadata["line_start"] = entity.location.start_line
                                version.metadata["line_end"] = entity.location.end_line

                                uow.logic_signatures.save(signature)

                                prev_versions = uow.logic_versions.list_by_signature(signature.id)
                                existing_ver = next((v for v in prev_versions if v.commit_hash == commit_hash), None)
                                if existing_ver:
                                    version.id = existing_ver.id
                                    uow.logic_evidence.delete_by_logic_version(existing_ver.id)
                                    prev_versions = [v for v in prev_versions if v.id != existing_ver.id]

                                if prev_versions:
                                    prev_versions.sort(key=lambda x: x.version_ordinal)
                                    latest_prev = prev_versions[-1]
                                    version.version_ordinal = latest_prev.version_ordinal + 1

                                    similarity = self._similarity_engine.compute_version_similarity(latest_prev, version)
                                    diff = self._diff_engine.diff_versions(latest_prev, version)

                                    if similarity >= 0.99:
                                        trans_type = TransitionType.UNCHANGED
                                    elif similarity >= 0.30:
                                        trans_type = TransitionType.EVOLVED
                                    else:
                                        trans_type = TransitionType.REPLACED

                                    transition = LogicTransition(
                                        id=uuid.uuid4(),
                                        from_logic_version_id=latest_prev.id,
                                        to_logic_version_id=version.id,
                                        transition_type=trans_type,
                                        similarity_score=similarity,
                                        overall_confidence=version.overall_confidence,
                                        metadata={
                                            "from_commit": latest_prev.commit_hash,
                                            "to_commit": version.commit_hash,
                                            "summary": diff.get("summary", ""),
                                            "dependency_hash": version.fingerprint.dependency_hash,
                                            "behavioral_hash": version.fingerprint.behavioral_hash,
                                        },
                                        created_at=datetime.utcnow(),
                                    )

                                    if existing_ver:
                                        existing_trans = uow.logic_transitions.get_by_to_version(existing_ver.id)
                                        if existing_trans:
                                            transition.id = existing_trans[0].id

                                    drift = self._drift_engine.compute_drift(transition, latest_prev, version)

                                    if existing_ver:
                                        existing_drift = uow.behavior_drift.get_by_transition(transition.id)
                                        if existing_drift:
                                            drift.id = existing_drift.id

                                    uow.logic_transitions.save(transition)
                                    uow.behavior_drift.save(drift)
                                else:
                                    version.version_ordinal = 1
                                    transition = LogicTransition(
                                        id=uuid.uuid4(),
                                        from_logic_version_id=None,
                                        to_logic_version_id=version.id,
                                        transition_type=TransitionType.CREATED,
                                        similarity_score=1.0,
                                        overall_confidence=version.overall_confidence,
                                        metadata={
                                            "to_commit": version.commit_hash,
                                            "summary": "First appearance of this behavioral logic in codebase.",
                                            "dependency_hash": version.fingerprint.dependency_hash,
                                            "behavioral_hash": version.fingerprint.behavioral_hash,
                                        },
                                        created_at=datetime.utcnow(),
                                    )

                                    if existing_ver:
                                        existing_trans = uow.logic_transitions.get_by_to_version(existing_ver.id)
                                        if existing_trans:
                                            transition.id = existing_trans[0].id

                                    uow.logic_transitions.save(transition)

                                if existing_ver:
                                    existing_exp = uow.behavior_explanations.get_by_logic_version(existing_ver.id)
                                    if existing_exp:
                                        explanation.id = existing_exp.id

                                uow.logic_versions.save(version)
                                uow.logic_evidence.save_batch(evidence_list)
                                uow.behavior_explanations.save(explanation)

                        uow.commit()

        finally:
            try:
                self._git_adapter.checkout_commit(local_path, default_branch)
            except Exception as e:
                print(f"[LogicOrchestrator] Failed to reset to branch {default_branch}: {e}")
