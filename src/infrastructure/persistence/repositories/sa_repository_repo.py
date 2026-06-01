"""SQLAlchemy implementation of IRepositoryRepository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.domain.entities.repository import RepositoryEntity
from src.domain.repositories.repository_repo import IRepositoryRepository
from src.domain.value_objects.repository_id import RepositoryId
from src.infrastructure.persistence.models.repository_model import RepositoryModel
from src.infrastructure.persistence.mappers.domain_mapper import DomainMapper


class SARepositoryRepository(IRepositoryRepository):
    """SQLAlchemy repository for Repository entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, id: RepositoryId) -> Optional[RepositoryEntity]:
        model = self.session.get(RepositoryModel, id.value)
        if model:
            return DomainMapper.to_repository_entity(model)
        return None

    def get_all(self) -> List[RepositoryEntity]:
        stmt = select(RepositoryModel)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_repository_entity(m) for m in models]

    def add(self, entity: RepositoryEntity) -> None:
        model = DomainMapper.to_repository_model(entity)
        self.session.add(model)

    def update(self, entity: RepositoryEntity) -> None:
        model = DomainMapper.to_repository_model(entity)
        self.session.merge(model)

    def delete(self, id: RepositoryId) -> None:
        model = self.session.get(RepositoryModel, id.value)
        if model:
            self.session.delete(model)
