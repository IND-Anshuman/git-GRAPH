"""SQLAlchemy models for accuracy and performance metrics."""

from datetime import datetime
import uuid
from sqlalchemy import String, Numeric, Integer, BigInteger, ForeignKey, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base

class BenchmarkReportModel(Base):
    """SQLAlchemy model representing a performance benchmark report."""
    
    __tablename__ = "temporal_benchmarks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    scan_duration_ms: Mapped[int] = mapped_column(Integer)
    diff_throughput_nodes_sec: Mapped[float] = mapped_column(Numeric(10, 2))
    reconstruction_latency_ms: Mapped[int] = mapped_column(Integer)
    db_size_bytes: Mapped[int] = mapped_column(BigInteger)
    memory_rss_bytes: Mapped[int] = mapped_column(BigInteger)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_temporal_benchmarks_repo", "repository_id"),
        Index("ix_temporal_benchmarks_commit", "commit_hash"),
    )

class AccuracyReportModel(Base):
    """SQLAlchemy model representing a validation accuracy report."""
    
    __tablename__ = "temporal_accuracy"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    rename_precision: Mapped[float] = mapped_column(Numeric(4, 3))
    rename_recall: Mapped[float] = mapped_column(Numeric(4, 3))
    move_precision: Mapped[float] = mapped_column(Numeric(4, 3))
    move_recall: Mapped[float] = mapped_column(Numeric(4, 3))
    event_accuracy: Mapped[float] = mapped_column(Numeric(4, 3))
    reconstruction_accuracy: Mapped[float] = mapped_column(Numeric(4, 3))
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_temporal_accuracy_repo", "repository_id"),
    )
