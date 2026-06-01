"""SQLAlchemy model for Code Entity."""

from typing import Any, Dict, Optional
import uuid

from sqlalchemy import String, Text, Integer, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base

class CodeEntityModel(Base):
    """SQLAlchemy model representing a code entity (class, function, etc.)."""
    
    __tablename__ = "code_entities"
    
    seid: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(255))
    qualified_name: Mapped[str] = mapped_column(String(1000))
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("source_files.id", ondelete="CASCADE"))
    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"))
    parent_seid: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("code_entities.seid", ondelete="SET NULL"), nullable=True
    )
    language: Mapped[str] = mapped_column(String(20))
    
    # Location
    file_path: Mapped[str] = mapped_column(Text)
    start_line: Mapped[int] = mapped_column(Integer)
    end_line: Mapped[int] = mapped_column(Integer)
    start_column: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    end_column: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Signatures
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    structural_fingerprint: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    source_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    
    __table_args__ = (
        Index("ix_code_entities_repo_type", "repository_id", "entity_type"),
        Index("ix_code_entities_repo_qname", "repository_id", "qualified_name"),
        Index("ix_code_entities_file_id", "file_id"),
        Index("ix_code_entities_parent_seid", "parent_seid"),
    )
