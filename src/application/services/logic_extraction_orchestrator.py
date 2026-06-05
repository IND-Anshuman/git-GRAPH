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
        # 1. Fetch Repository and Checkout commit
        with self._uow_factory() as uow:
            repo = uow.repositories.get_by_id(repository_id)
            if not repo:
                return

        self._git_adapter.checkout_commit(repo.local_path, commit_hash)

        # 2. Fetch the snapshot for this commit to find active entities
        with self._uow_factory() as uow:
            snapshot = uow.snapshots.get_by_commit(repository_id, commit_hash)
            if not snapshot:
                return
            entity_seids = list(snapshot.entity_seids)

        # 3. Iterate through active entities in the snapshot
        for seid in entity_seids:
            with self._uow_factory() as uow:
                entity = uow.code_entities.get_by_seid(seid)
                if not entity:
                    continue

                # We match patterns against functions and methods
                if entity.entity_type not in (EntityType.FUNCTION, EntityType.METHOD):
                    continue

                # 4. Read the containing file
                file_abs_path = os.path.join(repo.local_path, entity.location.file_path)
                if not os.path.exists(file_abs_path):
                    continue

                try:
                    with open(file_abs_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                except Exception:
                    continue

                # 5. Parse the file into a tree-sitter AST
                try:
                    parse_result = self._parser.parse_file(
                        entity.location.file_path, file_content, entity.language
                    )
                except Exception:
                    continue

                # 6. Extract logic items matching patterns
                extracted_items = self._extraction_engine.extract_logic(
                    entity, parse_result.tree, file_content, commit_hash
                )

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

                    # 7. Check if signature exists, and save
                    uow.logic_signatures.save(signature)

                    # 8. Link timeline to previous version
                    prev_versions = uow.logic_versions.list_by_signature(
                        signature.id
                    )

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

                        # Compute behavior drift
                        drift = self._drift_engine.compute_drift(
                            transition, latest_prev, version
                        )

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
                        uow.logic_transitions.save(transition)

                    # 9. Save Version, Evidence, and Explanation
                    uow.logic_versions.save(version)
                    uow.logic_evidence.save_batch(evidence_list)
                    uow.behavior_explanations.save(explanation)

                # Commit transaction for this entity
                uow.commit()
