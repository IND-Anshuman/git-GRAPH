from abc import ABC, abstractmethod

from src.domain.entities.change_event import ChangeEvent
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId

class IChangeEventRepository(ABC):
    """Interface for ChangeEvent repository operations."""

    @abstractmethod
    def save(self, event: ChangeEvent) -> None:
        """Persist a single change event."""
        pass

    @abstractmethod
    def save_batch(self, events: list[ChangeEvent]) -> None:
        """Persist a batch of change events."""
        pass

    @abstractmethod
    def get_by_commit(self, commit_hash: str) -> list[ChangeEvent]:
        """Fetch all change events introduced in a commit."""
        pass

    @abstractmethod
    def list_by_seid(self, seid: SEID) -> list[ChangeEvent]:
        """Fetch all change events that happened to a specific entity."""
        pass

    @abstractmethod
    def list_by_repository(self, repository_id: RepositoryId) -> list[ChangeEvent]:
        """Fetch all change events in a repository (timeline)."""
        pass
