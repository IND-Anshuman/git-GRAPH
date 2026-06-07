"""Service engine for mapping chronological concept evolution steps."""

import uuid
from typing import Dict, List, Set, Tuple
from datetime import datetime

from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.entities.concept_evolution import ConceptEvolution
from src.domain.enums.concept_transition_type import ConceptTransitionType
from src.domain.value_objects.repository_id import RepositoryId
from src.application.ports.unit_of_work import IUnitOfWork


class ConceptEvolutionEngine:
    """Detects historical split, merge, modification, and creation events between concept versions."""

    def track_evolution(
        self,
        uow: IUnitOfWork,
        repository_id: RepositoryId,
        commit_hash: str,
        detected_concepts: List[Tuple[ConceptNode, ConceptVersion, List[ConceptEvidence]]],
    ) -> List[ConceptEvolution]:
        """
        Derive evolution transition edges comparing current versions to predecessors.

        Args:
            uow: Active Unit of Work.
            repository_id: The repository identifier.
            commit_hash: The current Git commit.
            detected_concepts: Active concept versions detected at the current commit.

        Returns:
            A list of ConceptEvolution entities.
        """
        if not detected_concepts:
            return []

        namespace = uuid.UUID("f1a08555-de7b-49fa-98e6-d9b2cafac234")
        evolutions: List[ConceptEvolution] = []

        # 1. Resolve current concept SEID sets
        curr_concept_seids: Dict[uuid.UUID, Set[str]] = {}
        for c_node, c_ver, ev_list in detected_concepts:
            seids = set()
            for ev in ev_list:
                if ev.evidence_type == "LOGIC_VERSION":
                    l_ver = uow.logic_versions.get_by_id(ev.target_id)
                    if l_ver and l_ver.code_entity_seid:
                        seids.add(str(l_ver.code_entity_seid.value))
            curr_concept_seids[c_node.id] = seids

        # 2. Retrieve parent commit(s)
        # Search the commit database for the current commit's parent hashes
        parents = []
        cmt = uow.commits.get_by_hash(repository_id, commit_hash)
        if cmt and cmt.parent_hashes:
            parents = cmt.parent_hashes
        else:
            # Fallback: find commits in repository and sort chronologically to identify predecessor
            all_commits = uow.commits.list_by_repository(repository_id)
            all_commits.sort(key=lambda x: x.authored_date or x.committed_date)
            hashes = [c.hash for c in all_commits]
            if commit_hash in hashes:
                idx = hashes.index(commit_hash)
                if idx > 0:
                    parents = [hashes[idx - 1]]

        if not parents:
            # First commit: all detected concepts are CREATED
            for c_node, c_ver, _ in detected_concepts:
                evo_id = uuid.uuid5(namespace, f"evolution:{c_ver.id}:creation")
                evolutions.append(
                    ConceptEvolution(
                        id=evo_id,
                        from_concept_version_id=None,
                        to_concept_version_id=c_ver.id,
                        transition_type=ConceptTransitionType.CONCEPT_CREATION,
                        similarity_score=1.0,
                        created_at=datetime.utcnow(),
                    )
                )
            return evolutions

        # 3. Retrieve all concept versions active at the parent commit(s)
        parent_versions: List[ConceptVersion] = []
        for p_hash in parents:
            p_vers = uow.concept_versions.list_by_commit(repository_id, p_hash)
            parent_versions.extend(p_vers)

        # Map parent concept IDs to their SEID sets
        parent_concept_seids: Dict[uuid.UUID, Set[str]] = {}
        for p_ver in parent_versions:
            p_evs = uow.concept_evidence.list_by_concept_version(p_ver.id)
            seids = set()
            for ev in p_evs:
                if ev.evidence_type == "LOGIC_VERSION":
                    l_ver = uow.logic_versions.get_by_id(ev.target_id)
                    if l_ver and l_ver.code_entity_seid:
                        seids.add(str(l_ver.code_entity_seid.value))
            parent_concept_seids[p_ver.id] = seids

        parent_version_map = {v.id: v for v in parent_versions}

        # 4. Detect evolution transitions for each current concept version
        for c_node, c_ver, ev_list in detected_concepts:
            curr_seids = curr_concept_seids[c_node.id]
            if not curr_seids:
                continue

            matched_predecessor = False
            best_similarity = 0.0
            best_prev_ver_id = None
            split_candidates = []
            merge_candidates = []

            for p_ver_id, prev_seids in parent_concept_seids.items():
                if not prev_seids:
                    continue

                intersection = curr_seids.intersection(prev_seids)
                union = curr_seids.union(prev_seids)
                jaccard = len(intersection) / len(union) if union else 0.0

                p_ver = parent_version_map[p_ver_id]

                # Match candidate mapping to same concept
                if p_ver.concept_id == c_node.id:
                    matched_predecessor = True
                    best_similarity = jaccard
                    best_prev_ver_id = p_ver.id

                # Detect split/merge fractions
                # Split: V_prev splits to V_curr, meaning V_curr has >= 30% of V_prev's entities
                split_ratio = len(intersection) / len(prev_seids)
                # Merge: V_prev merges into V_curr, meaning V_prev has >= 30% of V_curr's entities
                merge_ratio = len(intersection) / len(curr_seids)

                if split_ratio >= 0.30 and p_ver.concept_id != c_node.id:
                    split_candidates.append((p_ver.id, jaccard))
                if merge_ratio >= 0.30 and p_ver.concept_id != c_node.id:
                    merge_candidates.append((p_ver.id, jaccard))

            if matched_predecessor:
                # Same concept exists: CONCEPT_MODIFICATION
                evo_id = uuid.uuid5(namespace, f"evolution:{best_prev_ver_id}:{c_ver.id}")
                evolutions.append(
                    ConceptEvolution(
                        id=evo_id,
                        from_concept_version_id=best_prev_ver_id,
                        to_concept_version_id=c_ver.id,
                        transition_type=ConceptTransitionType.CONCEPT_MODIFICATION,
                        similarity_score=best_similarity,
                        created_at=datetime.utcnow(),
                    )
                )
            elif split_candidates:
                # Inherited from parent splits: CONCEPT_SPLIT
                for p_id, sim in split_candidates:
                    evo_id = uuid.uuid5(namespace, f"evolution:{p_id}:{c_ver.id}:split")
                    evolutions.append(
                        ConceptEvolution(
                            id=evo_id,
                            from_concept_version_id=p_id,
                            to_concept_version_id=c_ver.id,
                            transition_type=ConceptTransitionType.CONCEPT_SPLIT,
                            similarity_score=sim,
                            created_at=datetime.utcnow(),
                        )
                    )
            elif merge_candidates:
                # Consolidated multiple parents: CONCEPT_MERGE
                for p_id, sim in merge_candidates:
                    evo_id = uuid.uuid5(namespace, f"evolution:{p_id}:{c_ver.id}:merge")
                    evolutions.append(
                        ConceptEvolution(
                            id=evo_id,
                            from_concept_version_id=p_id,
                            to_concept_version_id=c_ver.id,
                            transition_type=ConceptTransitionType.CONCEPT_MERGE,
                            similarity_score=sim,
                            created_at=datetime.utcnow(),
                        )
                    )
            else:
                # Fully new concept: CONCEPT_CREATION
                evo_id = uuid.uuid5(namespace, f"evolution:{c_ver.id}:creation")
                evolutions.append(
                    ConceptEvolution(
                        id=evo_id,
                        from_concept_version_id=None,
                        to_concept_version_id=c_ver.id,
                        transition_type=ConceptTransitionType.CONCEPT_CREATION,
                        similarity_score=1.0,
                        created_at=datetime.utcnow(),
                    )
                )

        return evolutions
