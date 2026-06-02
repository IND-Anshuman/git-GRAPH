"""SQLAlchemy model for Repository Snapshot."""

from datetime import datetime
from typing import Any, Dict, List
import uuid
from sqlalchemy import String, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.infrastructure.persistence.models.base import Base

class RepositorySnapshotModel(Base):
    """SQLAlchemy model representing a materialized snapshot checkpoint of the repository's code entities at a specific commit."""
    
    __tablename__ = "repository_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    commit_hash: Mapped[str] = mapped_column(
        ForeignKey("commits.hash", ondelete="CASCADE"), nullable=False
    )
    entity_seids: Mapped[List[str]] = mapped_column(JSON, default=list) # List of UUID strings
    snapshot_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    __table_args__ = (
        Index("ux_snapshots_repo_commit", "repository_id", "commit_hash", unique=True),
    )
