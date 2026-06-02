"""SQLAlchemy model for Commit."""

from datetime import datetime
import uuid
from sqlalchemy import String, Text, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base

class CommitModel(Base):
    """SQLAlchemy model representing a Git commit."""
    
    __tablename__ = "commits"

    hash: Mapped[str] = mapped_column(String(40), primary_key=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    author: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    message: Mapped[str] = mapped_column(Text)
    parent_hashes: Mapped[list[str]] = mapped_column(JSON, default=list)

    __table_args__ = (
        Index("ix_commits_repo_id", "repository_id"),
        Index("ix_commits_timestamp", "timestamp"),
    )
