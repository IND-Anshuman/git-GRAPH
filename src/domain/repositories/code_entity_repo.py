from abc import ABC, abstractmethod

from src.domain.entities.code_entity import CodeEntity
from src.domain.enums.entity_type import EntityType
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId

class ICodeEntityRepository(ABC):
    """Repository interface for managing CodeEntity."""

    @abstractmethod
    def save(self, entity: CodeEntity) -> None:
        pass

    @abstractmethod
    def save_batch(self, entities: list[CodeEntity]) -> None:
        pass

    @abstractmethod
    def get_by_seid(self, seid: SEID) -> CodeEntity | None:
        pass

    @abstractmethod
    def get_by_seids(self, seids: list[SEID]) -> list[CodeEntity]:
        pass

    @abstractmethod
    def get_by_repository(self, repo_id: RepositoryId, entity_type: EntityType | None = None) -> list[CodeEntity]:
        pass

    @abstractmethod
    def get_by_file(self, file_id: FileId) -> list[CodeEntity]:
        pass

    @abstractmethod
    def delete_by_repository(self, repo_id: RepositoryId) -> None:
        pass
