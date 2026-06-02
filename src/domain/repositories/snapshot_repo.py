from abc import ABC, abstractmethod

from src.domain.entities.repository_snapshot import RepositorySnapshot
from src.domain.value_objects.repository_id import RepositoryId

class IRepositorySnapshotRepository(ABC):
    """Interface for RepositorySnapshot repository operations."""

    @abstractmethod
    def save(self, snapshot: RepositorySnapshot) -> None:
        """Persist a repository snapshot checkpoint."""
        pass

    @abstractmethod
    def get_by_commit(self, repository_id: RepositoryId, commit_hash: str) -> RepositorySnapshot | None:
        """Fetch snapshot for a specific commit hash, if it exists."""
        pass

    @abstractmethod
    def get_latest_before_or_at_commits(self, repository_id: RepositoryId, commit_hashes: list[str]) -> RepositorySnapshot | None:
        """Find the latest snapshot corresponding to any commit in the list (ancestry path)."""
        pass
