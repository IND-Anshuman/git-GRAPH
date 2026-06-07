"""Use case for retrieving the concept dependency graph at a commit."""

import uuid
from typing import Callable, Optional
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId


class GetConceptRelationshipsUseCase:
    """Retrieves concept nodes and relationship edges for a repository concept map."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(self, repository_id: uuid.UUID, commit_hash: Optional[str] = None) -> dict:
        """
        Retrieves active concept nodes and relationships at a commit.

        Args:
            repository_id: The UUID of the repository.
            commit_hash: The target commit hash (falls back to last analyzed commit).

        Returns:
            A dictionary containing lists of 'nodes' and 'edges'.
        """
        repo_id = RepositoryId(repository_id)

        with self.uow_factory() as uow:
            repo = uow.repositories.get_by_id(repo_id)
            if not repo:
                raise ValueError(f"Repository {repository_id} not found.")

            target_commit = commit_hash or repo.metadata.get("last_analyzed_commit")
            if not target_commit:
                return {"nodes": [], "edges": []}

            versions = uow.concept_versions.list_by_commit(repo_id, target_commit)
            nodes_data = []
            active_node_ids = set()
            for ver in versions:
                node = uow.concept_nodes.get_by_id(ver.concept_id)
                if node:
                    nodes_data.append({"id": str(node.id), "label": node.name, "type": "Concept"})
                    active_node_ids.add(node.id)

            edges_data = []
            relationships = uow.concept_relationships.list_by_commit(repo_id, target_commit)
            for rel in relationships:
                if rel.from_concept_id in active_node_ids and rel.to_concept_id in active_node_ids:
                    edges_data.append(
                        {
                            "from": str(rel.from_concept_id),
                            "to": str(rel.to_concept_id),
                            "type": rel.relationship_type.value if hasattr(rel.relationship_type, "value") else str(rel.relationship_type),
                            "confidence": float(rel.confidence),
                        }
                    )

            return {"nodes": nodes_data, "edges": edges_data}
