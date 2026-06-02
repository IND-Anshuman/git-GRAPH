"""SQLAlchemy model for Change Event."""

from typing import Any, Dict
import uuid
from sqlalchemy import String, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base

class ChangeEventModel(Base):
    """SQLAlchemy model representing a semantic entity change event during a commit."""
    
    __tablename__ = "change_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    commit_hash: Mapped[str] = mapped_column(
        ForeignKey("commits.hash", ondelete="CASCADE"), nullable=False
    )
    seid: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("code_entities.seid", ondelete="CASCADE"), nullable=False
    )
    change_type: Mapped[str] = mapped_column(String(20))
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict)

    __table_args__ = (
        Index("ix_change_events_seid", "seid"),
        Index("ix_change_events_commit", "commit_hash"),
        Index("ix_change_events_repo", "repository_id"),
    )
