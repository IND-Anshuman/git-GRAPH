from abc import ABC, abstractmethod
import uuid

from src.domain.entities.entity_version import EntityVersion
from src.domain.value_objects.entity_id import SEID

class IEntityVersionRepository(ABC):
    """Interface for EntityVersion repository operations."""

    @abstractmethod
    def save(self, version: EntityVersion) -> None:
        """Persist a single entity version."""
        pass

    @abstractmethod
    def save_batch(self, versions: list[EntityVersion]) -> None:
        """Persist a list of entity versions in batch."""
        pass

    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> EntityVersion | None:
        """Fetch a specific entity version record by ID."""
        pass

    @abstractmethod
    def get_by_commit(self, commit_hash: str) -> list[EntityVersion]:
        """Fetch all entity versions introduced/captured in a commit."""
        pass

    @abstractmethod
    def get_by_commits(self, commit_hashes: list[str]) -> list[EntityVersion]:
        """Fetch all entity versions introduced/captured in a list of commits in batch."""
        pass

    @abstractmethod
    def get_latest_before_or_at(self, seid: SEID, commit_hash: str) -> EntityVersion | None:
        """Find the active version of an entity at or immediately before a given commit."""
        pass

    @abstractmethod
    def list_by_seid(self, seid: SEID) -> list[EntityVersion]:
        """Fetch the chronological evolution timeline of an entity by SEID."""
        pass
