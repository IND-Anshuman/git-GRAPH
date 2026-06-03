from abc import ABC, abstractmethod
from typing import Self
from src.domain.repositories import (
    IRepositoryRepository,
    ISourceFileRepository,
    ICodeEntityRepository,
    IRelationshipRepository,
    ICommitRepository,
    IEntityVersionRepository,
    IRelationshipVersionRepository,
    IChangeEventRepository,
    IRepositorySnapshotRepository,
    IMetricsRepository,
    IIntegrityRepository
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

    @property
    @abstractmethod
    def commits(self) -> ICommitRepository:
        pass

    @property
    @abstractmethod
    def entity_versions(self) -> IEntityVersionRepository:
        pass

    @property
    @abstractmethod
    def relationship_versions(self) -> IRelationshipVersionRepository:
        pass

    @property
    @abstractmethod
    def change_events(self) -> IChangeEventRepository:
        pass

    @property
    @abstractmethod
    def snapshots(self) -> IRepositorySnapshotRepository:
        pass

    @property
    @abstractmethod
    def metrics(self) -> IMetricsRepository:
        pass

    @property
    @abstractmethod
    def integrity(self) -> IIntegrityRepository:
        pass
