"""SQLAlchemy implementation of IRelationshipRepository."""

from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.domain.entities.relationship import Relationship
from src.domain.repositories.relationship_repo import IRelationshipRepository
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.entity_id import SEID
from src.domain.enums.relationship_type import RelationshipType
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

    def get_by_repository(self, repo_id: RepositoryId, rel_type: RelationshipType | None = None) -> List[Relationship]:
        if rel_type:
            stmt = select(RelationshipModel).where(
                RelationshipModel.repository_id == repo_id.value,
                RelationshipModel.relationship_type == rel_type.value
            )
        else:
            stmt = select(RelationshipModel).where(RelationshipModel.repository_id == repo_id.value)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_relationship_entity(m) for m in models]
        
    def get_by_source(self, seid: SEID) -> List[Relationship]:
        stmt = select(RelationshipModel).where(RelationshipModel.source_seid == seid.value)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_relationship_entity(m) for m in models]
        
    def get_by_target(self, seid: SEID) -> List[Relationship]:
        stmt = select(RelationshipModel).where(RelationshipModel.target_seid == seid.value)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_relationship_entity(m) for m in models]

    def save(self, rel: Relationship) -> None:
        model = DomainMapper.to_relationship_model(rel)
        self.session.merge(model)

    def save_batch(self, rels: List[Relationship]) -> None:
        models = [DomainMapper.to_relationship_model(r) for r in rels]
        for model in models:
            self.session.merge(model)

    def delete_by_repository(self, repo_id: RepositoryId) -> None:
        stmt = select(RelationshipModel).where(RelationshipModel.repository_id == repo_id.value)
        models = self.session.execute(stmt).scalars().all()
        for m in models:
            self.session.delete(m)
