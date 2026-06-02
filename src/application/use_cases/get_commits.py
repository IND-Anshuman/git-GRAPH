"""Use case for listing analyzed commits for a repository."""

from typing import Callable, List
import uuid

from src.application.ports.unit_of_work import IUnitOfWork
from src.application.dtos.responses import CommitResponse
from src.domain.value_objects.repository_id import RepositoryId

class GetCommitsUseCase:
    """Retrieves all analyzed commits for a repository."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(self, repository_id: str) -> List[CommitResponse]:
        """Fetch all commits for the given repository."""
        repo_id = RepositoryId(uuid.UUID(repository_id))
        with self.uow_factory() as uow:
            commits = uow.commits.list_by_repository(repo_id)
            return [
                CommitResponse(
                    hash=c.hash,
                    repository_id=str(c.repository_id),
                    author=c.author,
                    email=c.email,
                    timestamp=c.timestamp,
                    message=c.message,
                    parent_hashes=c.parent_hashes,
                    is_merge=c.is_merge,
                    is_root=c.is_root
                )
                for c in commits
            ]
