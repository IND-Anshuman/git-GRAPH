"""SQLAlchemy models for temporal graph integrity issues and repair audits."""

from datetime import datetime
import uuid
from sqlalchemy import String, Text, Boolean, JSON, ForeignKey, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base

class IntegrityViolationModel(Base):
    """SQLAlchemy model representing a temporal graph integrity failure or anomaly."""
    
    __tablename__ = "temporal_integrity_issues"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    violation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(10), nullable=False)
    target_seid: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    recommended_repair: Mapped[str] = mapped_column(Text)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_temporal_integrity_issues_repo", "repository_id"),
        Index("ix_temporal_integrity_issues_type", "violation_type"),
    )

class RepairAuditModel(Base):
    """SQLAlchemy model representing the execution audit of structural database fixes."""
    
    __tablename__ = "temporal_repair_audits"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    operator: Mapped[str] = mapped_column(String(100), nullable=False)
    issue_ids: Mapped[list[uuid.UUID]] = mapped_column(JSON, default=list)
    repair_actions: Mapped[list[dict]] = mapped_column(JSON, default=list)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_temporal_repair_audits_repo", "repository_id"),
    )
