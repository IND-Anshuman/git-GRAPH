"""Replay service for streaming forward/backward codebase evolution step-by-step."""

import logging
from typing import List, Dict, Any

from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId
from src.application.services.historical_reconstruction import HistoricalReconstructionService

logger = logging.getLogger(__name__)

class TemporalReplayService:
    """Streams commit-by-commit delta changes and exports visualizer-compliant graphs."""

    def __init__(self, reconstruction_service: HistoricalReconstructionService) -> None:
        self.reconstruction_service = reconstruction_service

    def get_timeline_replay(
        self,
        uow: IUnitOfWork,
        repository_id: RepositoryId,
        start_commit: str,
        end_commit: str
    ) -> List[Dict[str, Any]]:
        """Computes step-by-step diff states and network graph snapshots between two commits."""
        
        # 1. Fetch commits in chronological order
        commits = uow.commits.list_by_repository(repository_id)
        commit_hashes = [c.hash for c in commits]

        if start_commit not in commit_hashes or end_commit not in commit_hashes:
            raise ValueError("Start or end commit hash not found in repository history.")

        start_idx = commit_hashes.index(start_commit)
        end_idx = commit_hashes.index(end_commit)

        if start_idx > end_idx:
            # Replay backwards
            walk_range = range(start_idx, end_idx - 1, -1)
        else:
            # Replay forwards
            walk_range = range(start_idx, end_idx + 1)

        steps = []
        previous_entities = []
        previous_rels = []

        # Iterate step-by-step
        for idx in walk_range:
            current_hash = commit_hashes[idx]
            commit_entity = uow.commits.get_by_hash(current_hash)

            entities, rels = self.reconstruction_service.reconstruct_graph_at_commit(
                uow, repository_id, current_hash
            )

            # Map active entities and relationships
            current_entities_by_seid = {e.seid: e for e in entities}
            prev_entities_by_seid = {e.seid: e for e in previous_entities}

            # Node deltas
            added_nodes = []
            modified_nodes = []
            deleted_nodes = []

            for seid, ent in current_entities_by_seid.items():
                if seid not in prev_entities_by_seid:
                    added_nodes.append({
                        "seid": str(seid),
                        "name": ent.name,
                        "entity_type": ent.entity_type.name,
                        "file_path": ent.location.file_path
                    })
                else:
                    prev_ent = prev_entities_by_seid[seid]
                    if (
                        ent.name != prev_ent.name
                        or ent.location.file_path != prev_ent.location.file_path
                        or ent.content_hash != prev_ent.content_hash
                    ):
                        modified_nodes.append({
                            "seid": str(seid),
                            "name": ent.name,
                            "file_path": ent.location.file_path
                        })

            for seid, ent in prev_entities_by_seid.items():
                if seid not in current_entities_by_seid:
                    deleted_nodes.append({
                        "seid": str(seid),
                        "name": ent.name
                    })

            # Relationship link deltas
            current_rels_by_key = {(r.source_seid, r.target_seid, r.relationship_type): r for r in rels}
            prev_rels_by_key = {(r.source_seid, r.target_seid, r.relationship_type): r for r in previous_rels}

            added_links = []
            deleted_links = []

            for key, r in current_rels_by_key.items():
                if key not in prev_rels_by_key:
                    added_links.append({
                        "id": str(r.id),
                        "source": str(r.source_seid),
                        "target": str(r.target_seid),
                        "type": r.relationship_type.name
                    })

            for key, r in prev_rels_by_key.items():
                if key not in current_rels_by_key:
                    deleted_links.append({
                        "id": str(r.id),
                        "source": str(r.source_seid),
                        "target": str(r.target_seid),
                        "type": r.relationship_type.name
                    })

            # Standardized visualizer JSON Graph format export
            graph_export = {
                "nodes": [
                    {
                        "id": str(e.seid),
                        "name": e.name,
                        "type": e.entity_type.name,
                        "file": e.location.file_path
                    }
                    for e in entities
                ],
                "links": [
                    {
                        "id": str(r.id),
                        "source": str(r.source_seid),
                        "target": str(r.target_seid),
                        "type": r.relationship_type.name
                    }
                    for r in rels
                ]
            }

            steps.append({
                "commit_hash": current_hash,
                "message": commit_entity.message if commit_entity else "",
                "timestamp": commit_entity.timestamp.isoformat() if commit_entity else None,
                "delta": {
                    "added_nodes": added_nodes,
                    "modified_nodes": modified_nodes,
                    "deleted_nodes": deleted_nodes,
                    "added_links": added_links,
                    "deleted_links": deleted_links
                },
                "graph": graph_export
            })

            # Prepare for next comparison step
            previous_entities = entities
            previous_rels = rels

        return steps
