"""SQLAlchemy models for SEEE Evidence and Compiler Outputs."""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base

class SEEEEvidenceModel(Base):
    """SQLAlchemy model representing the raw SEEE EvidenceIR components extracted from a source file."""

    __tablename__ = "seee_evidence"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    
    # EvidenceIR fields stored as JSON
    symbol_graph: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    type_evidence: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    call_sites: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    dependency_graph: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    api_evidence: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    database_evidence: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    event_evidence: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    ai_evidence: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    flow_signatures: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    structure_signatures: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    raw_signals: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    diagnostics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    provenance: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_seee_evidence_file", "file_id"),
        Index("ix_seee_evidence_repo_commit", "repository_id", "commit_hash"),
    )


class CompilerOutputModel(Base):
    """SQLAlchemy model representing the unified Compiler Output of a source file."""

    __tablename__ = "compiler_outputs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)

    # Compiler output fields stored as JSON
    generated_entities: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    generated_relationships: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    report: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    frameworks_detected: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    semantic_hints: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_compiler_outputs_file", "file_id"),
        Index("ix_compiler_outputs_repo_commit", "repository_id", "commit_hash"),
    )
