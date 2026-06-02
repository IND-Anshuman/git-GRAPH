"""SQLAlchemy implementation of IRelationshipVersionRepository."""

from typing import List
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.domain.entities.relationship_version import RelationshipVersion
from src.domain.repositories.relationship_version_repo import IRelationshipVersionRepository
from src.infrastructure.persistence.models.relationship_version_model import RelationshipVersionModel
from src.infrastructure.persistence.mappers.domain_mapper import DomainMapper

class SARelationshipVersionRepository(IRelationshipVersionRepository):
    """SQLAlchemy repository for RelationshipVersion entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, version: RelationshipVersion) -> None:
        """Persist a single relationship version."""
        model = DomainMapper.to_relationship_version_model(version)
        self.session.merge(model)

    def save_batch(self, versions: list[RelationshipVersion]) -> None:
        """Persist a list of relationship versions in batch."""
        models = [DomainMapper.to_relationship_version_model(v) for v in versions]
        self.session.add_all(models)

    def get_by_commit(self, commit_hash: str) -> List[RelationshipVersion]:
        """Fetch all relationship changes introduced in a commit."""
        stmt = select(RelationshipVersionModel).where(RelationshipVersionModel.commit_hash == commit_hash)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_relationship_version_entity(m) for m in models]

    def list_by_relationship(self, relationship_id: uuid.UUID) -> List[RelationshipVersion]:
        """Fetch all changes for a specific relationship."""
        stmt = (
            select(RelationshipVersionModel)
            .where(RelationshipVersionModel.relationship_id == relationship_id)
            .order_by(RelationshipVersionModel.version_ordinal.asc())
        )
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_relationship_version_entity(m) for m in models]
