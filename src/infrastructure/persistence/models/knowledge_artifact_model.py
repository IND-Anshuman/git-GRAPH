"""SQLAlchemy model for Knowledge Artifact."""

from datetime import datetime
from typing import Any, Dict
import uuid

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base

class KnowledgeArtifactModel(Base):
    """SQLAlchemy model representing a temporal KnowledgeArtifact."""

    __tablename__ = "knowledge_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    artifact_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    valid_from_commit: Mapped[str] = mapped_column(String(40), nullable=False)
    valid_to_commit: Mapped[str] = mapped_column(String(40), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    artifact_version: Mapped[int] = mapped_column(nullable=False)
    provenance: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_knowledge_artifacts_repo", "repository_id"),
        Index("ix_knowledge_artifacts_type", "artifact_type"),
        Index("ix_knowledge_artifacts_commit_range", "repository_id", "valid_from_commit", "valid_to_commit"),
    )
