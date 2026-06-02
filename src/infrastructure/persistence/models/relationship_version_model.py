"""SQLAlchemy model for Relationship Version."""

from typing import Any, Dict
import uuid
from sqlalchemy import String, Integer, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base

class RelationshipVersionModel(Base):
    """SQLAlchemy model representing a relationship change version snapshot at a commit."""
    
    __tablename__ = "relationship_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    relationship_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("relationships.id", ondelete="CASCADE"), nullable=False
    )
    commit_hash: Mapped[str] = mapped_column(
        ForeignKey("commits.hash", ondelete="CASCADE"), nullable=False
    )
    mutation_type: Mapped[str] = mapped_column(String(20))
    version_ordinal: Mapped[int] = mapped_column(Integer)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict)

    __table_args__ = (
        Index("ix_relationship_versions_rel_ordinal", "relationship_id", "version_ordinal"),
        Index("ix_relationship_versions_commit", "commit_hash"),
    )
