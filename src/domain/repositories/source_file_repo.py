from abc import ABC, abstractmethod

from src.domain.entities.source_file import SourceFile
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId

class ISourceFileRepository(ABC):
    """Repository interface for managing SourceFile."""

    @abstractmethod
    def save(self, file: SourceFile) -> None:
        pass

    @abstractmethod
    def save_batch(self, files: list[SourceFile]) -> None:
        pass

    @abstractmethod
    def get_by_id(self, id: FileId) -> SourceFile | None:
        pass

    @abstractmethod
    def get_by_repository(self, repo_id: RepositoryId) -> list[SourceFile]:
        pass

    @abstractmethod
    def delete_by_repository(self, repo_id: RepositoryId) -> None:
        pass
