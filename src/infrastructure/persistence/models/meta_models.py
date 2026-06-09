"""SQLAlchemy models for dynamic Meta-Ontology and embedding registry tables."""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base


class MetaTypeModel(Base):
    """SQLAlchemy model representing a dynamically registered semantic type identifier."""

    __tablename__ = "meta_types"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)  # STRUCTURAL, BEHAVIORAL, CONCEPTUAL
    status: Mapped[str] = mapped_column(String(64), default="EXPERIMENTAL", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class MetaDefinitionModel(Base):
    """SQLAlchemy model representing a versioned schema structure configuration for a MetaType."""

    __tablename__ = "meta_definitions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    type_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("meta_types.id", ondelete="CASCADE"), nullable=False
    )
    major_version: Mapped[int] = mapped_column(Integer, nullable=False)
    minor_version: Mapped[int] = mapped_column(Integer, nullable=False)
    patch_version: Mapped[int] = mapped_column(Integer, nullable=False)
    schema_definition: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    semantic_signature: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_meta_defs_type", "type_id"),
        Index("uq_meta_defs_version", "type_id", "major_version", "minor_version", "patch_version", unique=True),
    )


class EmbeddingModelModel(Base):
    """SQLAlchemy model representing a vector model configuration registered in the EmbeddingRegistry."""

    __tablename__ = "embedding_models"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(256), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)  # local, openai, huggingface
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    distance_metric: Mapped[str] = mapped_column(String(32), nullable=False)  # cosine, l2, ip
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class EmbeddingVersionModel(Base):
    """SQLAlchemy model representing a specific registered configuration of an EmbeddingModel."""

    __tablename__ = "embedding_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    model_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("embedding_models.id", ondelete="CASCADE"), nullable=False
    )
    version_string: Mapped[str] = mapped_column(String(64), nullable=False)
    configuration: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("uq_embedding_version_model", "model_id", "version_string", unique=True),
    )
