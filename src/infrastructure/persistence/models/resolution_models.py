"""SQLAlchemy models for Semantic Resolution, Reasoning Governance, Structure/Architecture Graphs, and Cross-Repository dependencies."""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base


class SymbolGraphModel(Base):
    """SQLAlchemy model representing a node in the repository-wide symbol graph."""

    __tablename__ = "symbol_graph"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    symbol_id: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)  # 'CLASS', 'FUNCTION', etc.
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_symbol_graph_repo", "repository_id"),
        Index("ix_symbol_graph_canonical", "repository_id", "canonical_name"),
    )


class SymbolReferenceModel(Base):
    """SQLAlchemy model representing a relationship/reference edge in the symbol graph."""

    __tablename__ = "symbol_reference"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    source_symbol_id: Mapped[str] = mapped_column(String(255), nullable=False)
    target_symbol_id: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_type: Mapped[str] = mapped_column(String(64), nullable=False)  # 'CALLS', 'EXTENDS', etc.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_symbol_ref_repo", "repository_id"),
    )


class VariableFlowModel(Base):
    """SQLAlchemy model representing local variable assignments and lineage flow."""

    __tablename__ = "variable_flow"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    source_variable: Mapped[str] = mapped_column(String(255), nullable=False)
    target_variable: Mapped[str] = mapped_column(String(255), nullable=False)
    flow_type: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_variable_flow_repo", "repository_id"),
    )


class CrossFileResolutionModel(Base):
    """SQLAlchemy model representing resolved cross-file function/method calls."""

    __tablename__ = "cross_file_resolution"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    source_file: Mapped[str] = mapped_column(Text, nullable=False)
    source_entity: Mapped[str] = mapped_column(String(255), nullable=False)
    target_file: Mapped[str] = mapped_column(Text, nullable=False)
    target_entity: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_cross_file_res_repo", "repository_id"),
    )


class ExternalDependencyModel(Base):
    """SQLAlchemy model representing a third-party framework, API, model or service dependency."""

    __tablename__ = "external_dependency"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    dependency_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dependency_type: Mapped[str] = mapped_column(String(64), nullable=False)  # 'EXTERNAL_PACKAGE', etc.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_external_dep_repo", "repository_id"),
    )


class AIEvidenceModel(Base):
    """SQLAlchemy model representing specific evidence details for AI component discoveries."""

    __tablename__ = "ai_evidence"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    class_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    method_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pattern_matched: Mapped[str] = mapped_column(String(255), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_ai_evidence_repo", "repository_id"),
    )


class RepositoryArchitectureGraphModel(Base):
    """SQLAlchemy model representing high-level architecture nodes (Domains, Bounded Contexts, Services, External Systems)."""

    __tablename__ = "repository_architecture_graph"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    node_id: Mapped[str] = mapped_column(String(255), nullable=False)
    node_name: Mapped[str] = mapped_column(String(255), nullable=False)
    node_type: Mapped[str] = mapped_column(String(64), nullable=False)  # 'DOMAIN', 'BOUNDED_CONTEXT', 'SERVICE', 'EXTERNAL_SYSTEM'
    owner_team: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_repo_arch_repo", "repository_id"),
        Index("ix_repo_arch_node", "repository_id", "node_id"),
    )


class ArchitectureRelationshipModel(Base):
    """SQLAlchemy model representing relationship edges between architecture nodes."""

    __tablename__ = "architecture_relationship"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    source_node_id: Mapped[str] = mapped_column(String(255), nullable=False)
    target_node_id: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(64), nullable=False)  # 'CONTAINS', 'OWNS', 'CALLS', 'DEPENDS_ON'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_arch_rel_repo", "repository_id"),
    )


class RepositoryStructureGraphModel(Base):
    """SQLAlchemy model representing File/Module/Package/Namespace structure relationships."""

    __tablename__ = "repository_structure_graph"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    source_file_path: Mapped[str] = mapped_column(Text, nullable=False)
    target_file_path: Mapped[str] = mapped_column(Text, nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(64), nullable=False)  # 'CONTAINS', 'EXPORTS', 'IMPORTS', 'REFERENCES'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_repo_struct_repo", "repository_id"),
    )


class CompilerOutputVersionModel(Base):
    """SQLAlchemy model representing compiler engine & rules version used for generating compiler outputs."""

    __tablename__ = "compiler_output_version"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    compiler_version: Mapped[str] = mapped_column(String(64), nullable=False)
    rules_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_comp_out_ver_repo", "repository_id"),
    )


class ReasoningArtifactModel(Base):
    """SQLAlchemy model representing LLM-generated reasoning facts with governance fields."""

    __tablename__ = "reasoning_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    artifact_type: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    validation_status: Mapped[str] = mapped_column(String(64), default="PROPOSED", nullable=False)  # 'PROPOSED', 'VERIFIED', etc.
    evidence_refs: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    supporting_entities: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    supporting_relationships: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    supporting_behaviors: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_reasoning_art_repo", "repository_id"),
    )


class KnowledgeDriftModel(Base):
    """SQLAlchemy model representing macro architecture and high-level concept drift tracking."""

    __tablename__ = "knowledge_drifts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    drift_type: Mapped[str] = mapped_column(String(64), nullable=False)  # 'ARCHITECTURE_DRIFT', 'CONCEPT_DRIFT'
    element_id: Mapped[str] = mapped_column(String(255), nullable=False)
    from_value: Mapped[str] = mapped_column(Text, nullable=False)
    to_value: Mapped[str] = mapped_column(Text, nullable=False)
    drift_score: Mapped[float] = mapped_column(Float, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_knowledge_drift_repo", "repository_id"),
    )


class ExternalKnowledgeReferenceModel(Base):
    """SQLAlchemy model representing cross-repository API or dependency dependencies."""

    __tablename__ = "external_knowledge_references"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    source_repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    target_repository_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dependency_type: Mapped[str] = mapped_column(String(64), nullable=False)  # 'API_CONSUMPTION', 'PACKAGE_IMPORT'
    api_endpoint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_ext_know_ref_repo", "source_repository_id"),
    )
