from abc import ABC, abstractmethod

from src.domain.entities.commit import Commit
from src.domain.value_objects.repository_id import RepositoryId

class ICommitRepository(ABC):
    """Interface for Commit repository operations."""

    @abstractmethod
    def save(self, commit: Commit) -> None:
        """Persist a commit entity."""
        pass

    @abstractmethod
    def get_by_hash(self, commit_hash: str) -> Commit | None:
        """Fetch a commit by its hash."""
        pass

    @abstractmethod
    def list_by_repository(self, repository_id: RepositoryId) -> list[Commit]:
        """Fetch all commits for a specific repository, ordered chronologically."""
        pass
