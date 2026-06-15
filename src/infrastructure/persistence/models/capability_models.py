"""SQLAlchemy models for the Capability Intelligence Layer (CIL) (Phase 6)."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
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
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.persistence.models.base import Base

class CapabilityModel(Base):
    """SQLAlchemy model representing a verified capability."""
    __tablename__ = "capabilities"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    capability_type: Mapped[str] = mapped_column(String(64), nullable=False)
    maturity_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    coverage_score: Mapped[float] = mapped_column(Float, default=0.0)
    concepts: Mapped[List[str]] = mapped_column(JSON, default=list)
    behaviors: Mapped[List[str]] = mapped_column(JSON, default=list)
    flows: Mapped[List[str]] = mapped_column(JSON, default=list)
    entities: Mapped[List[str]] = mapped_column(JSON, default=list)
    relationships: Mapped[List[str]] = mapped_column(JSON, default=list)
    coverage: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_capabilities_repository", "repository_id"),
    )


class CapabilityCandidateModel(Base):
    """SQLAlchemy model representing a proposed capability candidate."""
    __tablename__ = "capability_candidates"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="CANDIDATE")
    evidence: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    capability_type: Mapped[str] = mapped_column(String(64), default="TECHNICAL")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_candidates_repository", "repository_id"),
    )


class CapabilityRelationshipModel(Base):
    """SQLAlchemy model representing a relationship between two capabilities."""
    __tablename__ = "capability_relationships"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    source_capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    target_capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(64), nullable=False)
    dependency_type: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_relationships_repository", "repository_id"),
    )


class CapabilityFingerprintModel(Base):
    """SQLAlchemy model representing a capability signature fingerprint."""
    __tablename__ = "capability_fingerprints"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False)
    concept_signature: Mapped[str] = mapped_column(String(64), nullable=False)
    behavior_signature: Mapped[str] = mapped_column(String(64), nullable=False)
    flow_signature: Mapped[str] = mapped_column(String(64), nullable=False)
    relationship_signature: Mapped[str] = mapped_column(String(64), nullable=False)
    architecture_signature: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_fingerprints_capability", "capability_id"),
    )


class CapabilityEvolutionModel(Base):
    """SQLAlchemy model representing capability history mutations."""
    __tablename__ = "capability_evolution"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    capability_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_evolution_repository", "repository_id"),
    )


class CapabilityTimelineModel(Base):
    """SQLAlchemy model representing capability active features per commit."""
    __tablename__ = "capability_timelines"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    features: Mapped[List[str]] = mapped_column(JSON, default=list)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_timelines_capability", "capability_id"),
    )


class CapabilityDependencyModel(Base):
    """SQLAlchemy model representing dependency mapping details between capabilities."""
    __tablename__ = "capability_dependencies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    source_capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    target_capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    dependency_type: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_dependencies_repository", "repository_id"),
    )


class CapabilityHealthModel(Base):
    """SQLAlchemy model representing capability health and coverage scores."""
    __tablename__ = "capability_health"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False)
    coverage_score: Mapped[float] = mapped_column(Float, default=0.0)
    ownership_score: Mapped[float] = mapped_column(Float, default=0.0)
    dependency_score: Mapped[float] = mapped_column(Float, default=0.0)
    complexity_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_health_capability", "capability_id"),
    )


class CapabilityBlastRadiusModel(Base):
    """SQLAlchemy model representing capability modification blast radius reports."""
    __tablename__ = "capability_blast_radius"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False)
    blast_radius_score: Mapped[float] = mapped_column(Float, default=0.0)
    impacted_capabilities: Mapped[List[str]] = mapped_column(JSON, default=list)
    impacted_services: Mapped[List[str]] = mapped_column(JSON, default=list)
    impacted_apis: Mapped[List[str]] = mapped_column(JSON, default=list)
    impacted_agents: Mapped[List[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_blast_radius_capability", "capability_id"),
    )


class CapabilityProvenanceModel(Base):
    """SQLAlchemy model representing capability origin explainability logs."""
    __tablename__ = "capability_provenance"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False)
    source_concepts: Mapped[List[str]] = mapped_column(JSON, default=list)
    source_behaviors: Mapped[List[str]] = mapped_column(JSON, default=list)
    source_flows: Mapped[List[str]] = mapped_column(JSON, default=list)
    source_entities: Mapped[List[str]] = mapped_column(JSON, default=list)
    discovery_algorithm: Mapped[str] = mapped_column(String(64), nullable=False)
    discovery_version: Mapped[str] = mapped_column(String(32), nullable=False)
    placement_score: Mapped[float] = mapped_column(Float, default=0.0)
    creation_commit: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_provenance_capability", "capability_id"),
    )


class CapabilityConfidenceModel(Base):
    """SQLAlchemy model representing capability confidence ratings."""
    __tablename__ = "capability_confidence"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_strength: Mapped[float] = mapped_column(Float, nullable=False)
    flow_cohesion: Mapped[float] = mapped_column(Float, nullable=False)
    concept_agreement: Mapped[float] = mapped_column(Float, nullable=False)
    behavior_agreement: Mapped[float] = mapped_column(Float, nullable=False)
    relationship_density: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_confidence_capability", "capability_id"),
    )


class CapabilityOverlapModel(Base):
    """SQLAlchemy model representing detected duplicate capabilities."""
    __tablename__ = "capability_overlap"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    capability_a_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    capability_b_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    overlap_score: Mapped[float] = mapped_column(Float, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_overlap_repository", "repository_id"),
    )


class CapabilityStabilityModel(Base):
    """SQLAlchemy model representing stability index mappings."""
    __tablename__ = "capability_stability"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False)
    stability_score: Mapped[float] = mapped_column(Float, nullable=False)
    stability_status: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_stability_capability", "capability_id"),
    )


class CapabilitySnapshotModel(Base):
    """SQLAlchemy model representing the capability reasoning snapshot cache."""
    __tablename__ = "capability_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    risk: Mapped[str] = mapped_column(String(64), nullable=False)
    health: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    owners: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    dependencies: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    flows: Mapped[List[str]] = mapped_column(JSON, default=list)
    timeline: Mapped[List[str]] = mapped_column(JSON, default=list)
    drift: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_snapshots_capability", "capability_id"),
    )


class CapabilityBoundaryModel(Base):
    """SQLAlchemy model representing Bounded Context boundary mapping metrics."""
    __tablename__ = "capability_boundaries"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False)
    internal_entities: Mapped[int] = mapped_column(Integer, nullable=False)
    external_dependencies: Mapped[int] = mapped_column(Integer, nullable=False)
    boundary_strength: Mapped[float] = mapped_column(Float, nullable=False)
    leakage_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_boundaries_capability", "capability_id"),
    )


class CapabilityCohesionModel(Base):
    """SQLAlchemy model representing capability cohesion scores."""
    __tablename__ = "capability_cohesion"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False)
    internal_flow_density: Mapped[float] = mapped_column(Float, nullable=False)
    internal_concept_similarity: Mapped[float] = mapped_column(Float, nullable=False)
    internal_behavior_similarity: Mapped[float] = mapped_column(Float, nullable=False)
    cohesion_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_cohesion_capability", "capability_id"),
    )


class CapabilityCouplingModel(Base):
    """SQLAlchemy model representing capability coupling metrics."""
    __tablename__ = "capability_coupling"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False)
    api_coupling: Mapped[float] = mapped_column(Float, nullable=False)
    database_coupling: Mapped[float] = mapped_column(Float, nullable=False)
    event_coupling: Mapped[float] = mapped_column(Float, nullable=False)
    shared_service_coupling: Mapped[float] = mapped_column(Float, nullable=False)
    shared_entity_coupling: Mapped[float] = mapped_column(Float, nullable=False)
    coupling_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_coupling_capability", "capability_id"),
    )


class CapabilityEmbeddingModel(Base):
    """SQLAlchemy model representing capability vector embeddings."""
    __tablename__ = "capability_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    capability_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False)
    embedding: Mapped[List[float]] = mapped_column(JSON, nullable=False)  # Store vector values
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_embeddings_capability", "capability_id"),
    )


class CapabilityTaxonomyCandidateModel(Base):
    """SQLAlchemy model representing learned categories proposed for promotion."""
    __tablename__ = "capability_taxonomy_candidates"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    suggested_category: Mapped[str] = mapped_column(String(256), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_capability_taxonomy_candidates_repository", "repository_id"),
    )
