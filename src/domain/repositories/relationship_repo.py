from abc import ABC, abstractmethod

from src.domain.entities.relationship import Relationship
from src.domain.enums.relationship_type import RelationshipType
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId

class IRelationshipRepository(ABC):
    """Repository interface for managing Relationship."""

    @abstractmethod
    def save(self, rel: Relationship) -> None:
        pass

    @abstractmethod
    def save_batch(self, rels: list[Relationship]) -> None:
        pass

    @abstractmethod
    def get_by_repository(self, repo_id: RepositoryId, rel_type: RelationshipType | None = None) -> list[Relationship]:
        pass

    @abstractmethod
    def get_by_source(self, seid: SEID) -> list[Relationship]:
        pass

    @abstractmethod
    def get_by_target(self, seid: SEID) -> list[Relationship]:
        pass

    @abstractmethod
    def delete_by_repository(self, repo_id: RepositoryId) -> None:
        pass
