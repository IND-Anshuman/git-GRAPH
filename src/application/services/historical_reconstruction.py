"""Historical reconstruction service for rebuilding the graph at any commit."""

import uuid
from typing import Dict, List, Set, Tuple

from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.relationship import Relationship
from src.domain.enums.mutation_type import MutationType
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation

class HistoricalReconstructionService:
    """Orchestrates historical graph state reconstruction at a target commit hash."""

    def reconstruct_graph_at_commit(
        self,
        uow: IUnitOfWork,
        repository_id: RepositoryId,
        target_commit_hash: str
    ) -> Tuple[List[CodeEntity], List[Relationship]]:
        """Reconstructs the active entities and relationships of a repository at a target commit.
        
        Uses materialized checkpoints (snapshots) and replays change events to compute state.
        """
        # 1. Fetch chronological list of commits up to target_commit_hash
        # To get the ancestry path, we start from target_commit_hash and trace parents back to root.
        ancestry_list = self._get_ancestry_path(uow, target_commit_hash)
        if not ancestry_list:
            raise ValueError(f"Target commit hash {target_commit_hash} not found in database.")

        # Reverse registry: oldest is first, target_commit is last
        chronological_walk = list(ancestry_list)
        chronological_walk.reverse()

        # 2. Query latest snapshot along this ancestry path
        snapshot = uow.snapshots.get_latest_before_or_at_commits(repository_id, ancestry_list)
        
        entities_state: Dict[SEID, CodeEntity] = {}
        relationships_state: Dict[uuid.UUID, Relationship] = {}
        
        start_index = 0
        if snapshot:
            # Reconstruct starting state from checkpoint snapshot data
            # Snapshot data contains: {"entities": [serialized...], "relationships": [serialized...]}
            for data in snapshot.snapshot_data.get("entities", []):
                entity = uow.code_entities.get_by_seid(SEID.from_string(data["seid"]))
                if entity:
                    entities_state[entity.seid] = entity
                    
            for data in snapshot.snapshot_data.get("relationships", []):
                rel_id = uuid.UUID(data["id"])
                # Fetch relationship
                stmt = uow.relationships.get_by_id(rel_id)
                if stmt:
                    relationships_state[rel_id] = stmt
            
            # Find index of snapshot commit in chronological walk
            snapshot_hash = snapshot.commit_hash
            if snapshot_hash in chronological_walk:
                start_index = chronological_walk.index(snapshot_hash) + 1

        # 3. Walk forward and apply change events
        for i in range(start_index, len(chronological_walk)):
            commit_hash = chronological_walk[i]
            
            # Apply entity version changes
            entity_versions = uow.entity_versions.get_by_commit(commit_hash)
            for ev in entity_versions:
                if ev.mutation_type == MutationType.CREATED:
                    # Fetch template CodeEntity
                    entity = uow.code_entities.get_by_seid(ev.seid)
                    if entity:
                        # Override values to match this version
                        entity.name = ev.canonical_name
                        entity.qualified_name = ev.canonical_name
                        entity.location = CodeLocation(
                            file_path=ev.file_path,
                            start_line=ev.start_line,
                            end_line=ev.end_line,
                            start_column=entity.location.start_column if entity.location else None,
                            end_column=entity.location.end_column if entity.location else None
                        )
                        entity.content_hash = ev.content_hash
                        entity.source_text = ev.source_text
                        entities_state[ev.seid] = entity
                elif ev.mutation_type == MutationType.DELETED:
                    if ev.seid in entities_state:
                        del entities_state[ev.seid]
                elif ev.mutation_type in (MutationType.MODIFIED, MutationType.RENAMED, MutationType.MOVED):
                    if ev.seid in entities_state:
                        entity = entities_state[ev.seid]
                        entity.name = ev.canonical_name.split(".")[-1] # Simple name
                        entity.qualified_name = ev.canonical_name
                        entity.location = CodeLocation(
                            file_path=ev.file_path,
                            start_line=ev.start_line,
                            end_line=ev.end_line,
                            start_column=entity.location.start_column if entity.location else None,
                            end_column=entity.location.end_column if entity.location else None
                        )
                        entity.content_hash = ev.content_hash
                        entity.source_text = ev.source_text
                        entity.metadata.update(ev.metadata)

            # Apply relationship version changes
            rel_versions = uow.relationship_versions.get_by_commit(commit_hash)
            for rv in rel_versions:
                if rv.mutation_type == MutationType.CREATED:
                    rel = uow.relationships.get_by_id(rv.relationship_id)
                    if rel:
                        relationships_state[rv.relationship_id] = rel
                elif rv.mutation_type == MutationType.DELETED:
                    if rv.relationship_id in relationships_state:
                        del relationships_state[rv.relationship_id]

        # 4. Filter relationships whose source or target entities no longer exist (dangling protection)
        valid_rels = []
        for rel in relationships_state.values():
            if rel.source_seid in entities_state and rel.target_seid in entities_state:
                valid_rels.append(rel)

        return list(entities_state.values()), valid_rels

    def _get_ancestry_path(self, uow: IUnitOfWork, target_hash: str) -> List[str]:
        """Traces commit hierarchy from target commit back to root parent.
        
        Returns a list of commit hashes ordered from target_hash to root.
        """
        ancestry = []
        current = target_hash
        visited = set()
        
        while current and current not in visited:
            visited.add(current)
            commit = uow.commits.get_by_hash(current)
            if not commit:
                break
            ancestry.append(current)
            if commit.parent_hashes:
                # Prioritize first parent for linear traversal path representation
                current = commit.parent_hashes[0]
            else:
                current = None
        return ancestry
