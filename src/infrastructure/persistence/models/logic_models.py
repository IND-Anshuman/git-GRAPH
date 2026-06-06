"""SQLAlchemy models for Phase 3 Behavioral Intelligence entities."""

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
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.models.base import Base


class OntologyNodeModel(Base):
    """SQLAlchemy model representing a node in the hierarchical behavior classification tree."""

    __tablename__ = "ontology_nodes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    node_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    domain: Mapped[str] = mapped_column(String(64), nullable=False)
    parent_node_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    is_leaf: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ontology_version: Mapped[str] = mapped_column(String(20), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_ontology_nodes_domain", "domain"),
        Index("ix_ontology_nodes_parent", "parent_node_id"),
    )


class BehaviorPatternModel(Base):
    """SQLAlchemy model representing a loaded detection pattern rule."""

    __tablename__ = "behavior_patterns"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    pattern_id: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    pattern_version: Mapped[str] = mapped_column(String(20), nullable=False)
    ontology_node_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("ontology_nodes.node_id", ondelete="RESTRICT"), nullable=False
    )
    base_confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    index_keys: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    rules: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    schema_version: Mapped[str] = mapped_column(String(10), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_behavior_patterns_ontology_node", "ontology_node_id"),
        Index("ix_behavior_patterns_pattern_id", "pattern_id"),
    )


class LogicSignatureModel(Base):
    """SQLAlchemy model representing a stable behavioral signature scoped to a repository."""

    __tablename__ = "logic_signatures"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    entity_seid: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_name: Mapped[str] = mapped_column(String(512), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    primary_ontology_node_id: Mapped[Optional[str]] = mapped_column(
        String(128), ForeignKey("ontology_nodes.node_id", ondelete="SET NULL"), nullable=True
    )
    overall_confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_logic_signatures_entity_seid", "entity_seid"),
        Index("ix_logic_signatures_entity_type", "entity_type"),
        Index("ix_logic_signatures_repository", "repository_id"),
    )


class LogicVersionModel(Base):
    """SQLAlchemy model representing a logic implementation snapshot at a commit."""

    __tablename__ = "logic_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    signature_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("logic_signatures.id", ondelete="CASCADE"), nullable=False
    )
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    index_keys: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    ast_fingerprint: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    complexity_score: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    line_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    line_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    raw_source_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_logic_versions_commit_hash", "commit_hash"),
        Index("ix_logic_versions_signature", "signature_id"),
    )


class LogicEvidenceModel(Base):
    """SQLAlchemy model representing a single piece of evidence supporting a logic version detection."""

    __tablename__ = "logic_evidence"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("logic_versions.id", ondelete="CASCADE"), nullable=False
    )
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False)
    pattern_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    matched_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    line_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    column_offset: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_logic_evidence_evidence_type", "evidence_type"),
        Index("ix_logic_evidence_pattern_id", "pattern_id"),
        Index("ix_logic_evidence_version", "version_id"),
    )


class LogicTransitionModel(Base):
    """SQLAlchemy model representing a behavioral transition edge between two logic versions."""

    __tablename__ = "logic_transitions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    from_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("logic_versions.id", ondelete="SET NULL"), nullable=True
    )
    to_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("logic_versions.id", ondelete="CASCADE"), nullable=False
    )
    transition_type: Mapped[str] = mapped_column(String(64), nullable=False)
    from_commit_hash: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    to_commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    similarity_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    drift_magnitude: Mapped[Optional[float]] = mapped_column(Numeric(6, 4), nullable=True)
    is_breaking_change: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_logic_transitions_from_version", "from_version_id"),
        Index("ix_logic_transitions_to_commit", "to_commit_hash"),
        Index("ix_logic_transitions_to_version", "to_version_id"),
        Index("ix_logic_transitions_type", "transition_type"),
    )


class BehaviorExplanationModel(Base):
    """SQLAlchemy model representing a human-readable behavior explanation verdict details."""

    __tablename__ = "behavior_explanations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("logic_versions.id", ondelete="CASCADE"), nullable=False
    )
    explanation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    security_implications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    generated_by: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_behavior_explanations_type", "explanation_type"),
        Index("ix_behavior_explanations_version", "version_id"),
    )


class BehaviorDriftModel(Base):
    """SQLAlchemy model representing computed fine-grained behavioral drift details."""

    __tablename__ = "behavior_drift"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    transition_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("logic_transitions.id", ondelete="CASCADE"), nullable=False
    )
    baseline_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("logic_versions.id", ondelete="CASCADE"), nullable=False
    )
    current_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("logic_versions.id", ondelete="CASCADE"), nullable=False
    )
    drift_score: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    drift_category: Mapped[str] = mapped_column(String(64), nullable=False)
    ontology_shift: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    from_ontology_node_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    to_ontology_node_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    pattern_additions: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    pattern_removals: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    pattern_modifications: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_behavior_drift_category", "drift_category"),
        Index("ix_behavior_drift_current_version", "current_version_id"),
        Index("ix_behavior_drift_transition", "transition_id"),
    )


class LogicClusterModel(Base):
    """SQLAlchemy model representing a logic cluster grouping logic signatures."""

    __tablename__ = "logic_clusters"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    cluster_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    cluster_label: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    ontology_node_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    centroid_fingerprint: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    member_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cohesion_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_logic_clusters_ontology_node", "ontology_node_id"),
    )


class LogicClusterMemberModel(Base):
    """SQLAlchemy model representing membership linking signatures to logic clusters."""

    __tablename__ = "logic_cluster_members"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    cluster_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("logic_clusters.id", ondelete="CASCADE"), nullable=False
    )
    signature_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("logic_signatures.id", ondelete="CASCADE"), nullable=False
    )
    distance_to_centroid: Mapped[Optional[float]] = mapped_column(Numeric(6, 4), nullable=True)
    is_centroid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_logic_cluster_members_cluster", "cluster_id"),
        Index("ix_logic_cluster_members_signature", "signature_id"),
    )


class LogicVersionPatternModel(Base):
    """SQLAlchemy model representing many-to-many relationship of logic versions to behavior patterns."""

    __tablename__ = "logic_version_patterns"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("logic_versions.id", ondelete="CASCADE"), nullable=False
    )
    behavior_pattern_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("behavior_patterns.id", ondelete="CASCADE"), nullable=False
    )
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_logic_version_patterns_behavior_pattern", "behavior_pattern_id"),
        Index("ix_logic_version_patterns_version", "version_id"),
    )
