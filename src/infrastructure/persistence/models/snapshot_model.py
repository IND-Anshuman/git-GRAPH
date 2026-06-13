"""SQLAlchemy model for Repository Snapshot."""

from datetime import datetime
from typing import Any, Dict, List, Optional
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
    entity_count: Mapped[int] = mapped_column(default=0, server_default="0", nullable=False)
    relationship_count: Mapped[int] = mapped_column(default=0, server_default="0", nullable=False)
    behavior_count: Mapped[int] = mapped_column(default=0, server_default="0", nullable=False)
    concept_count: Mapped[int] = mapped_column(default=0, server_default="0", nullable=False)
    capability_count: Mapped[int] = mapped_column(default=0, server_default="0", nullable=False)
    dependency_graph_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    __table_args__ = (
        Index("ux_snapshots_repo_commit", "repository_id", "commit_hash", unique=True),
    )
