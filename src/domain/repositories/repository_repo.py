from abc import ABC, abstractmethod

from src.domain.entities.repository import RepositoryEntity
from src.domain.value_objects.repository_id import RepositoryId

class IRepositoryRepository(ABC):
    """Repository interface for managing RepositoryEntity."""

    @abstractmethod
    def save(self, entity: RepositoryEntity) -> None:
        pass

    @abstractmethod
    def get_by_id(self, id: RepositoryId) -> RepositoryEntity | None:
        pass

    @abstractmethod
    def get_by_url(self, url: str) -> RepositoryEntity | None:
        pass

    @abstractmethod
    def list_all(self) -> list[RepositoryEntity]:
        pass

    @abstractmethod
    def delete(self, id: RepositoryId) -> None:
        pass
