"""SQLAlchemy implementation of ICodeEntityRepository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.domain.entities.code_entity import CodeEntity
from src.domain.repositories.code_entity_repo import ICodeEntityRepository
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.file_id import FileId
from src.infrastructure.persistence.models.code_entity_model import CodeEntityModel
from src.infrastructure.persistence.mappers.domain_mapper import DomainMapper


class SACodeEntityRepository(ICodeEntityRepository):
    """SQLAlchemy repository for CodeEntity entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, id: SEID) -> Optional[CodeEntity]:
        model = self.session.get(CodeEntityModel, id.value)
        if model:
            return DomainMapper.to_code_entity(model)
        return None

    def get_all_by_repository(self, repository_id: RepositoryId) -> List[CodeEntity]:
        stmt = select(CodeEntityModel).where(CodeEntityModel.repository_id == repository_id.value)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_code_entity(m) for m in models]
        
    def get_all_by_file(self, file_id: FileId) -> List[CodeEntity]:
        stmt = select(CodeEntityModel).where(CodeEntityModel.file_id == file_id.value)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_code_entity(m) for m in models]

    def add(self, entity: CodeEntity) -> None:
        model = DomainMapper.to_code_entity_model(entity)
        self.session.add(model)

    def add_many(self, entities: List[CodeEntity]) -> None:
        models = [DomainMapper.to_code_entity_model(e) for e in entities]
        self.session.add_all(models)

    def update(self, entity: CodeEntity) -> None:
        model = DomainMapper.to_code_entity_model(entity)
        self.session.merge(model)

    def delete(self, id: SEID) -> None:
        model = self.session.get(CodeEntityModel, id.value)
        if model:
            self.session.delete(model)
