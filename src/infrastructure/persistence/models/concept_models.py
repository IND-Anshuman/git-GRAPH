"""SQLAlchemy models for Phase 4 Concept Graph and Concept Intelligence entities."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.models.base import Base
from src.domain.enums.concept_relationship_type import ConceptRelationshipType
from src.domain.enums.concept_transition_type import ConceptTransitionType


class ConceptNodeModel(Base):
    """SQLAlchemy model representing a unique high-level concept."""

    __tablename__ = "concept_nodes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    ontology_node_id: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system_defined: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_concept_nodes_repository", "repository_id"),
        Index("ix_concept_nodes_ontology_node", "ontology_node_id"),
        Index("uq_repo_ontology_node", "repository_id", "ontology_node_id", unique=True),
    )


class ConceptVersionModel(Base):
    """SQLAlchemy model representing a point-in-time version of a concept at a commit."""

    __tablename__ = "concept_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("concept_nodes.id", ondelete="CASCADE"), nullable=False
    )
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_concept_versions_concept", "concept_id"),
        Index("ix_concept_versions_commit", "commit_hash"),
        Index("ix_concept_versions_concept_commit", "concept_id", "commit_hash", unique=True),
    )


class ConceptEvidenceModel(Base):
    """SQLAlchemy model linking concept versions to underlying logic evidences."""

    __tablename__ = "concept_evidence"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    concept_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("concept_versions.id", ondelete="CASCADE"), nullable=False
    )
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)  # UUID of logic_versions or logic_evidence
    confidence_contribution: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_concept_evidence_version", "concept_version_id"),
        Index("ix_concept_evidence_target", "target_id"),
    )


class ConceptRelationshipModel(Base):
    """SQLAlchemy model representing a directed relationship between concepts at a commit."""

    __tablename__ = "concept_relationships"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    from_concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("concept_nodes.id", ondelete="CASCADE"), nullable=False
    )
    to_concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("concept_nodes.id", ondelete="CASCADE"), nullable=False
    )
    relationship_type: Mapped[ConceptRelationshipType] = mapped_column(
        Enum(ConceptRelationshipType), nullable=False
    )
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_concept_relationships_repository_commit", "repository_id", "commit_hash"),
        Index("ix_concept_relationships_from", "from_concept_id"),
        Index("ix_concept_relationships_to", "to_concept_id"),
    )


class ConceptClusterModel(Base):
    """SQLAlchemy model representing high-level capability grouping clusters."""

    __tablename__ = "concept_clusters"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    cluster_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    cluster_label: Mapped[str] = mapped_column(String(256), nullable=False)
    cohesion_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    member_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class ConceptClusterMemberModel(Base):
    """SQLAlchemy model defining members inside concept clusters."""

    __tablename__ = "concept_cluster_members"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    cluster_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("concept_clusters.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("concept_nodes.id", ondelete="CASCADE"), nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_concept_cluster_members_cluster", "cluster_id"),
        Index("ix_concept_cluster_members_concept", "concept_id"),
        Index("uq_cluster_concept", "cluster_id", "concept_id", unique=True),
    )


class ConceptExplanationModel(Base):
    """SQLAlchemy model representing structured explanation text summaries and triggers."""

    __tablename__ = "concept_explanations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    concept_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("concept_versions.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    detail: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ConceptMetricsModel(Base):
    """SQLAlchemy model storing degree, betweenness centrality, PageRank, and size metrics."""

    __tablename__ = "concept_metrics"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    concept_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("concept_versions.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    entity_count: Mapped[int] = mapped_column(Integer, nullable=False)
    file_count: Mapped[int] = mapped_column(Integer, nullable=False)
    in_degree: Mapped[int] = mapped_column(Integer, nullable=False)
    out_degree: Mapped[int] = mapped_column(Integer, nullable=False)
    degree_centrality: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    betweenness_centrality: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    pagerank_score: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    impact_score: Mapped[float] = mapped_column(Numeric(8, 3), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ConceptDriftModel(Base):
    """SQLAlchemy model representing calculated conceptual drift values."""

    __tablename__ = "concept_drift"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("concept_nodes.id", ondelete="CASCADE"), nullable=False
    )
    baseline_commit: Mapped[str] = mapped_column(String(40), nullable=False)
    current_commit: Mapped[str] = mapped_column(String(40), nullable=False)
    drift_score: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    drift_category: Mapped[str] = mapped_column(String(64), nullable=False)
    dimension_scores: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_concept_drift_concept", "concept_id"),
    )


class ConceptEvolutionModel(Base):
    """SQLAlchemy model representing chronological transitions between concept versions."""

    __tablename__ = "concept_evolution"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    from_concept_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("concept_versions.id", ondelete="SET NULL"), nullable=True
    )
    to_concept_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("concept_versions.id", ondelete="CASCADE"), nullable=False
    )
    transition_type: Mapped[ConceptTransitionType] = mapped_column(
        Enum(ConceptTransitionType), nullable=False
    )
    similarity_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_concept_evolution_to", "to_concept_version_id"),
    )
