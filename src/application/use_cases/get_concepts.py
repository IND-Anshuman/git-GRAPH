"""Use case for querying active concepts of a repository at a commit."""

import uuid
from typing import Callable, List, Optional
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId


class GetConceptsUseCase:
    """Retrieves concepts matching repository, commit, and domain filters."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(self, repository_id: uuid.UUID, commit_hash: Optional[str] = None, domain: Optional[str] = None) -> List[dict]:
        """
        Retrieves active concepts for a given commit.

        Args:
            repository_id: The UUID of the repository.
            commit_hash: The target commit hash (falls back to last analyzed commit).
            domain: Optional top-level domain filter (e.g. 'security').

        Returns:
            A list of serialized concept dictionaries.
        """
        repo_id = RepositoryId(repository_id)

        with self.uow_factory() as uow:
            repo = uow.repositories.get_by_id(repo_id)
            if not repo:
                raise ValueError(f"Repository {repository_id} not found.")

            target_commit = commit_hash or repo.metadata.get("last_analyzed_commit")
            if not target_commit:
                return []

            versions = uow.concept_versions.list_by_commit(target_commit)
            results = []
            for ver in versions:
                node = uow.concept_nodes.get_by_id(ver.concept_id)
                if not node:
                    continue

                if domain and not node.ontology_node_id.startswith(domain):
                    continue

                results.append(
                    {
                        "id": str(node.id),
                        "ontology_node_id": node.ontology_node_id,
                        "name": node.name,
                        "confidence": float(ver.confidence),
                        "is_active": ver.is_active,
                        "created_at": node.created_at,
                    }
                )

            return results
