"""SQLAlchemy implementation of IRelationshipRepository."""

from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.domain.entities.relationship import Relationship
from src.domain.repositories.relationship_repo import IRelationshipRepository
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.entity_id import SEID
from src.infrastructure.persistence.models.relationship_model import RelationshipModel
from src.infrastructure.persistence.mappers.domain_mapper import DomainMapper


class SARelationshipRepository(IRelationshipRepository):
    """SQLAlchemy repository for Relationship entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, id: uuid.UUID) -> Optional[Relationship]:
        model = self.session.get(RelationshipModel, id)
        if model:
            return DomainMapper.to_relationship_entity(model)
        return None

    def get_all_by_repository(self, repository_id: RepositoryId) -> List[Relationship]:
        stmt = select(RelationshipModel).where(RelationshipModel.repository_id == repository_id.value)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_relationship_entity(m) for m in models]
        
    def get_by_source(self, source_seid: SEID) -> List[Relationship]:
        stmt = select(RelationshipModel).where(RelationshipModel.source_seid == source_seid.value)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_relationship_entity(m) for m in models]
        
    def get_by_target(self, target_seid: SEID) -> List[Relationship]:
        stmt = select(RelationshipModel).where(RelationshipModel.target_seid == target_seid.value)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_relationship_entity(m) for m in models]

    def add(self, entity: Relationship) -> None:
        model = DomainMapper.to_relationship_model(entity)
        self.session.add(model)

    def add_many(self, entities: List[Relationship]) -> None:
        models = [DomainMapper.to_relationship_model(e) for e in entities]
        self.session.add_all(models)

    def update(self, entity: Relationship) -> None:
        model = DomainMapper.to_relationship_model(entity)
        self.session.merge(model)

    def delete(self, id: uuid.UUID) -> None:
        model = self.session.get(RelationshipModel, id)
        if model:
            self.session.delete(model)
