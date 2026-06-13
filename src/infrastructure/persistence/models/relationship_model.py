"""SQLAlchemy model for Relationship."""

from typing import Any, Dict
import uuid

from sqlalchemy import String, JSON, ForeignKey, Float, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base

class RelationshipModel(Base):
    """SQLAlchemy model representing a relationship between code entities."""
    
    __tablename__ = "relationships"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"))
    relationship_type: Mapped[str] = mapped_column(String(30))
    source_seid: Mapped[uuid.UUID] = mapped_column(ForeignKey("code_entities.seid", ondelete="CASCADE"))
    target_seid: Mapped[uuid.UUID] = mapped_column(ForeignKey("code_entities.seid", ondelete="CASCADE"))
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    layer: Mapped[str] = mapped_column(String(30), default="STRUCTURAL", server_default="STRUCTURAL", nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    
    __table_args__ = (
        Index("ix_relationships_source_type", "source_seid", "relationship_type"),
        Index("ix_relationships_target_type", "target_seid", "relationship_type"),
        Index("ix_relationships_repo_type", "repository_id", "relationship_type"),
        UniqueConstraint("source_seid", "target_seid", "relationship_type", name="uq_relationship"),
    )
