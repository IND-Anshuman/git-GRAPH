"""SQLAlchemy model for Entity Version."""

from typing import Any, Dict, Optional
import uuid
from sqlalchemy import String, Text, Integer, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base

class EntityVersionModel(Base):
    """SQLAlchemy model representing an entity version snapshot at a commit."""
    
    __tablename__ = "entity_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    seid: Mapped[uuid.UUID] = mapped_column(ForeignKey("code_entities.seid", ondelete="CASCADE"), nullable=False)
    commit_hash: Mapped[str] = mapped_column(ForeignKey("commits.hash", ondelete="CASCADE"), nullable=False)
    version_ordinal: Mapped[int] = mapped_column(Integer)
    mutation_type: Mapped[str] = mapped_column(String(20))
    canonical_name: Mapped[str] = mapped_column(String(1000))
    file_path: Mapped[str] = mapped_column(Text)
    start_line: Mapped[int] = mapped_column(Integer)
    end_line: Mapped[int] = mapped_column(Integer)
    content_hash: Mapped[str] = mapped_column(String(64))
    structural_fingerprint: Mapped[str] = mapped_column(String(64))
    source_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict)

    __table_args__ = (
        Index("ix_entity_versions_seid_ordinal", "seid", "version_ordinal"),
        Index("ix_entity_versions_commit", "commit_hash"),
        Index("ux_entity_versions_seid_commit", "seid", "commit_hash", unique=True),
    )
