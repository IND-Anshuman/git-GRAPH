"""SQLAlchemy models for the Architectural Intelligence Layer (AIL) (Phase 7B)."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.persistence.models.base import Base


class ArchitectureProfileModel(Base):
    __tablename__ = "architecture_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[str] = mapped_column(String(256), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    architecture_type: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    evidence: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_architecture_profiles_repo", "repository_id"),
        Index("ix_architecture_profiles_repo_commit", "repository_id", "commit_hash"),
    )


class ArchitectureSnapshotModel(Base):
    __tablename__ = "architecture_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[str] = mapped_column(String(256), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    architecture_profiles: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    fitness_metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    violations: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    ownership_profile: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_architecture_snapshots_repo", "repository_id"),
        Index("ix_architecture_snapshots_repo_commit", "repository_id", "commit_hash"),
    )


class ArchitectureFitnessModel(Base):
    __tablename__ = "architecture_fitness"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[str] = mapped_column(String(256), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    coupling_score: Mapped[float] = mapped_column(Float, nullable=False)
    cohesion_score: Mapped[float] = mapped_column(Float, nullable=False)
    instability_score: Mapped[float] = mapped_column(Float, nullable=False)
    abstractness_score: Mapped[float] = mapped_column(Float, nullable=False)
    distance_from_main_sequence: Mapped[float] = mapped_column(Float, nullable=False)
    cyclicity_score: Mapped[float] = mapped_column(Float, nullable=False)
    layer_violation_score: Mapped[float] = mapped_column(Float, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    formulas: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_architecture_fitness_repo", "repository_id"),
    )


class ArchitectureViolationModel(Base):
    __tablename__ = "architecture_violations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[str] = mapped_column(String(256), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    rule_name: Mapped[str] = mapped_column(String(256), nullable=False)
    severity: Mapped[str] = mapped_column(String(64), nullable=False)
    affected_entities: Mapped[List[str]] = mapped_column(JSON, default=list)
    affected_capabilities: Mapped[List[str]] = mapped_column(JSON, default=list)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_architecture_violations_repo", "repository_id"),
    )


class ArchitectureInvariantModel(Base):
    __tablename__ = "architecture_invariants"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True) # Optional if global
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    rule_expression: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(64), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    source_role: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    forbidden_target_role: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_architecture_invariants_repo", "repository_id"),
    )


class ArchitectureDriftModel(Base):
    __tablename__ = "architecture_drifts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[str] = mapped_column(String(256), nullable=False)
    drift_type: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_state: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    current_state: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    delta: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    from_commit: Mapped[str] = mapped_column(String(40), nullable=False)
    to_commit: Mapped[str] = mapped_column(String(40), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_architecture_drifts_repo", "repository_id"),
    )


class ArchitectureTimelineModel(Base):
    __tablename__ = "architecture_timelines"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[str] = mapped_column(String(256), nullable=False)
    entries: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_architecture_timelines_repo", "repository_id"),
    )


class ArchitectureBenchmarkModel(Base):
    __tablename__ = "architecture_benchmarks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[str] = mapped_column(String(256), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    current_fitness: Mapped[float] = mapped_column(Float, nullable=False)
    comparison_group: Mapped[str] = mapped_column(String(256), nullable=False)
    comparison_avg_fitness: Mapped[float] = mapped_column(Float, nullable=False)
    percentile_rank: Mapped[float] = mapped_column(Float, nullable=False)
    key_gaps: Mapped[List[str]] = mapped_column(JSON, default=list)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_architecture_benchmarks_repo", "repository_id"),
    )


class ArchitectureSimilarityModel(Base):
    __tablename__ = "architecture_similarities"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    source_repository_id: Mapped[str] = mapped_column(String(256), nullable=False)
    target_repository_id: Mapped[str] = mapped_column(String(256), nullable=False)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    topology_similarity: Mapped[float] = mapped_column(Float, nullable=False)
    dependency_similarity: Mapped[float] = mapped_column(Float, nullable=False)
    capability_similarity: Mapped[float] = mapped_column(Float, nullable=False)
    flow_similarity: Mapped[float] = mapped_column(Float, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_architecture_similarities_source", "source_repository_id"),
        Index("ix_architecture_similarities_target", "target_repository_id"),
    )


class OwnershipProfileModel(Base):
    __tablename__ = "ownership_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[str] = mapped_column(String(256), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    capability_ownership: Mapped[Dict[str, List[str]]] = mapped_column(JSON, default=dict)
    knowledge_silos: Mapped[List[str]] = mapped_column(JSON, default=list)
    bus_factor_risks: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    unowned_capabilities: Mapped[List[str]] = mapped_column(JSON, default=list)
    overloaded_teams: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    ownership_drift: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    evidence_sources: Mapped[List[str]] = mapped_column(JSON, default=list)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_ownership_profiles_repo", "repository_id"),
    )


class RefactoringCandidateModel(Base):
    __tablename__ = "refactoring_candidates"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[str] = mapped_column(String(256), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    candidate_type: Mapped[str] = mapped_column(String(64), nullable=False)
    priority: Mapped[str] = mapped_column(String(64), nullable=False)
    target_entities: Mapped[List[str]] = mapped_column(JSON, default=list)
    evidence: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    expected_benefit: Mapped[str] = mapped_column(Text, nullable=False)
    fitness_impact: Mapped[float] = mapped_column(Float, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_refactoring_candidates_repo", "repository_id"),
    )


class ArchitectureRecommendationModel(Base):
    __tablename__ = "architecture_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[str] = mapped_column(String(256), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    recommendation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_elements: Mapped[List[str]] = mapped_column(JSON, default=list)
    action_description: Mapped[str] = mapped_column(Text, nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    expected_fitness_delta: Mapped[float] = mapped_column(Float, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_architecture_recommendations_repo", "repository_id"),
    )
