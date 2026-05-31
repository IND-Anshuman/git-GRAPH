from abc import ABC, abstractmethod
from typing import Self
from src.domain.repositories import (
    IRepositoryRepository,
    ISourceFileRepository,
    ICodeEntityRepository,
    IRelationshipRepository
)

class IUnitOfWork(ABC):
    @abstractmethod
    def __enter__(self) -> Self:
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @property
    @abstractmethod
    def repositories(self) -> IRepositoryRepository:
        pass

    @property
    @abstractmethod
    def source_files(self) -> ISourceFileRepository:
        pass

    @property
    @abstractmethod
    def code_entities(self) -> ICodeEntityRepository:
        pass

    @property
    @abstractmethod
    def relationships(self) -> IRelationshipRepository:
        pass
