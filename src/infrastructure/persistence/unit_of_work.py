"""SQLAlchemy implementation of Unit of Work."""

from typing import Any
from sqlalchemy.orm import Session

from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.repositories.repository_repo import IRepositoryRepository
from src.domain.repositories.source_file_repo import ISourceFileRepository
from src.domain.repositories.code_entity_repo import ICodeEntityRepository
from src.domain.repositories.relationship_repo import IRelationshipRepository

from src.infrastructure.persistence.repositories.sa_repository_repo import SARepositoryRepository
from src.infrastructure.persistence.repositories.sa_source_file_repo import SASourceFileRepository
from src.infrastructure.persistence.repositories.sa_code_entity_repo import SACodeEntityRepository
from src.infrastructure.persistence.repositories.sa_relationship_repo import SARelationshipRepository
from src.infrastructure.persistence.database import DatabaseEngine


class SQLAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy implementation of the Unit of Work pattern."""

    def __init__(self, db_engine: DatabaseEngine) -> None:
        self._db_engine = db_engine
        self._session: Session = None
        
    def __enter__(self) -> "SQLAlchemyUnitOfWork":
        self._session = self._db_engine.session_factory()
        self.repositories = SARepositoryRepository(self._session)
        self.source_files = SASourceFileRepository(self._session)
        self.code_entities = SACodeEntityRepository(self._session)
        self.relationships = SARelationshipRepository(self._session)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            if exc_type is not None:
                self.rollback()
        finally:
            self._session.close()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
