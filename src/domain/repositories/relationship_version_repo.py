from abc import ABC, abstractmethod
import uuid

from src.domain.entities.relationship_version import RelationshipVersion

class IRelationshipVersionRepository(ABC):
    """Interface for RelationshipVersion repository operations."""

    @abstractmethod
    def save(self, version: RelationshipVersion) -> None:
        """Persist a single relationship version."""
        pass

    @abstractmethod
    def save_batch(self, versions: list[RelationshipVersion]) -> None:
        """Persist a list of relationship versions in batch."""
        pass

    @abstractmethod
    def get_by_commit(self, commit_hash: str) -> list[RelationshipVersion]:
        """Fetch all relationship changes introduced in a commit."""
        pass

    @abstractmethod
    def get_by_commits(self, commit_hashes: list[str]) -> list[RelationshipVersion]:
        """Fetch all relationship changes introduced in a list of commits in batch."""
        pass

    @abstractmethod
    def list_by_relationship(self, relationship_id: uuid.UUID) -> list[RelationshipVersion]:
        """Fetch all changes for a specific relationship."""
        pass
