"""
Phase 7C — Pydantic Schemas for Decision Intelligence Layer API.

All schemas use:
    - model_config = ConfigDict(from_attributes=True) for ORM compatibility.
    - Explicit field types (no 'Any' in response models).
    - Optional fields with sensible defaults for nullable database columns.
    - Field descriptions for OpenAPI documentation generation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ─── Evidence ─────────────────────────────────────────────────────────────────

class DecisionEvidenceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    supporting_commits: List[str] = Field(default_factory=list, description="Commit hashes that evidence this decision")
    supporting_documents: List[str] = Field(default_factory=list, description="ADR document IDs confirming this decision")
    supporting_capabilities: List[str] = Field(default_factory=list, description="Capability IDs affected by this decision")
    supporting_architecture_changes: List[str] = Field(default_factory=list, description="Architecture change event IDs")
    supporting_repository_events: List[str] = Field(default_factory=list, description="Raw RepositoryEvent IDs")


# ─── Confidence ───────────────────────────────────────────────────────────────

class DecisionConfidenceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: float = Field(description="Overall weighted confidence score [0.0, 1.0]")
    evidence_coverage: float = Field(description="How many commits carry the signal")
    historical_support: float = Field(description="How many distinct events support it")
    architectural_support: float = Field(description="ADR document confirmation strength")
    capability_support: float = Field(description="Capability co-occurrence strength")
    artifact_agreement: float = Field(description="ADR status agreement score")


# ─── Decision Version ─────────────────────────────────────────────────────────

class DecisionVersionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(None, description="Version record UUID")
    decision_id: str = Field(description="Parent decision UUID")
    version: int = Field(description="Version number (1-indexed)")
    commit_hash: Optional[str] = Field(None, description="Commit hash at which this version was recorded")
    confidence: Optional[float] = Field(None, description="Confidence score at this version")
    supporting_evidence: Optional[List[str]] = Field(None, description="Evidence commits for this version")
    generated_at: Optional[datetime] = Field(None, description="When this version record was generated")


# ─── Decision (core) ──────────────────────────────────────────────────────────

class DecisionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Unique decision identifier")
    name: str = Field(description="Human-readable decision name")
    description: str = Field(description="Explanation of the decision and its context")
    decision_type: str = Field(description="One of the DecisionType enum values")
    status: str = Field(description="One of the DecisionStatus enum values")
    confidence_score: Optional[float] = Field(None, description="Overall confidence score [0.0, 1.0]")
    first_seen_commit: Optional[str] = Field(None, description="First commit hash where this decision was detected")
    last_seen_commit: Optional[str] = Field(None, description="Most recent commit hash for this decision")
    repository_id: str = Field(description="Repository this decision belongs to")
    created_at: Optional[datetime] = Field(None, description="When the decision record was created")
    updated_at: Optional[datetime] = Field(None, description="When the decision record was last updated")


class DecisionDetailSchema(DecisionSchema):
    """Extended schema with versions, evidence, and fitness."""

    versions: List[DecisionVersionSchema] = Field(default_factory=list, description="All recorded versions")
    evidence: Optional[DecisionEvidenceSchema] = Field(None, description="Full evidence record")
    fitness: Optional["DecisionFitnessSchema"] = Field(None, description="Latest fitness evaluation")
    conflicts: List["DecisionConflictSchema"] = Field(default_factory=list, description="Known conflicts")


class DecisionCreate(BaseModel):
    name: str = Field(description="Decision name")
    description: str = Field(description="Decision description")
    decision_type: str = Field(description="DecisionType enum value")
    status: str = Field(description="DecisionStatus enum value")
    repository_id: str = Field(description="Target repository ID")
    confidence_score: Optional[float] = Field(None, description="Initial confidence score")
    first_seen_commit: Optional[str] = Field(None, description="First commit hash")
    last_seen_commit: Optional[str] = Field(None, description="Last commit hash")


# ─── Decision Fitness ─────────────────────────────────────────────────────────

class DecisionFitnessSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    decision_id: Optional[str] = Field(None, description="Parent decision UUID")
    longevity_score: float = Field(description="How long the decision has been active [0.0, 1.0]")
    stability_score: float = Field(description="Inverse of version churn rate [0.0, 1.0]")
    impact_score: float = Field(description="Breadth of architectural impact [0.0, 1.0]")
    adoption_score: float = Field(description="Evidence density (commits + documents) [0.0, 1.0]")
    success_rate: float = Field(description="Composite health proxy [0.0, 1.0]")
    overall_fitness: float = Field(description="Weighted overall fitness score [0.0, 1.0]")
    evaluated_at: Optional[datetime] = Field(None, description="When the fitness was evaluated")
    fitness_rating: str = Field(default="UNKNOWN", description="Human label: EXCELLENT / GOOD / FAIR / POOR / CRITICAL")

    @classmethod
    def from_orm_with_rating(cls, orm_obj: object) -> "DecisionFitnessSchema":
        """Build schema and compute fitness_rating from overall_fitness."""
        schema = cls.model_validate(orm_obj)
        score = schema.overall_fitness
        if score >= 0.80:
            schema = schema.model_copy(update={"fitness_rating": "EXCELLENT"})
        elif score >= 0.65:
            schema = schema.model_copy(update={"fitness_rating": "GOOD"})
        elif score >= 0.45:
            schema = schema.model_copy(update={"fitness_rating": "FAIR"})
        elif score >= 0.25:
            schema = schema.model_copy(update={"fitness_rating": "POOR"})
        else:
            schema = schema.model_copy(update={"fitness_rating": "CRITICAL"})
        return schema


# ─── Decision Conflict ────────────────────────────────────────────────────────

class DecisionConflictSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(None, description="Conflict record UUID")
    decision_a_id: str = Field(description="First conflicting decision UUID")
    decision_b_id: str = Field(description="Second conflicting decision UUID")
    conflict_type: Optional[str] = Field(None, description="Type of conflict (e.g. STATUS_CONFLICT, EVIDENCE_OVERLAP)")
    description: Optional[str] = Field(None, description="Human-readable conflict description")
    severity: Optional[float] = Field(None, description="Conflict severity [0.0, 1.0]")
    detected_at: Optional[datetime] = Field(None, description="When the conflict was detected")


# ─── Intent ───────────────────────────────────────────────────────────────────

class IntentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Unique intent identifier")
    name: str = Field(description="Human-readable intent label")
    intent_type: str = Field(description="One of the IntentType enum values")
    description: Optional[str] = Field(None, description="Description of the strategic intent")
    confidence_score: Optional[float] = Field(None, description="Confidence score [0.0, 1.0]")
    supporting_decisions: Optional[List[str]] = Field(None, description="Decision IDs motivating this intent")
    repository_id: str = Field(description="Repository this intent belongs to")
    first_seen_at: Optional[datetime] = Field(None, description="When this intent first appeared")
    last_seen_at: Optional[datetime] = Field(None, description="When this intent was last observed")


# ─── Causal Relationship ──────────────────────────────────────────────────────

class CausalRelationshipSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(None, description="Causal relationship UUID")
    chain_id: Optional[str] = Field(None, description="Parent chain UUID")
    cause_id: str = Field(description="UUID of the cause node (Intent or Decision)")
    effect_id: str = Field(description="UUID of the effect node (Decision or Capability)")
    cause_label: Optional[str] = Field(None, description="Human-readable cause label")
    effect_label: Optional[str] = Field(None, description="Human-readable effect label")
    relationship_type: Optional[str] = Field(None, description="MOTIVATES | ENABLES | CONTRADICTS")
    confidence: Optional[float] = Field(None, description="Relationship confidence [0.0, 1.0]")
    evidence: Optional[List[str]] = Field(None, description="Evidence items supporting this relationship")


class CausalChainSchema(BaseModel):
    """A complete causal chain rooted at an intent."""

    chain_id: str = Field(description="Chain UUID")
    repository_id: str = Field(description="Repository this chain belongs to")
    root_cause_id: str = Field(description="UUID of the root cause (typically an Intent)")
    summary: str = Field(description="Human-readable summary of the chain")
    confidence: float = Field(description="Average chain confidence [0.0, 1.0]")
    generated_at: Optional[datetime] = Field(None, description="When the chain was computed")
    relationships: List[CausalRelationshipSchema] = Field(
        default_factory=list,
        description="All relationships in this chain",
    )


# ─── Technology Lifecycle ─────────────────────────────────────────────────────

class TechnologyLifecycleSchema(BaseModel):
    technology_key: str = Field(description="Normalised technology identifier")
    display_name: str = Field(description="Human-readable technology name")
    adoption_decision_id: str = Field(description="UUID of the adoption decision")
    removal_decision_id: Optional[str] = Field(None, description="UUID of the removal decision, if retired")
    adoption_commit: Optional[str] = Field(None, description="First commit where adoption was detected")
    removal_commit: Optional[str] = Field(None, description="Last commit where removal was detected")
    repository_id: str = Field(description="Repository this lifecycle belongs to")
    status: str = Field(description="ACTIVE | RETIRED | PROPOSED")
    stability_index: float = Field(description="Stability score [0.0, 1.0]")
    lifespan_days: Optional[int] = Field(None, description="Days between adoption and removal (None if still active)")
    supporting_commits: List[str] = Field(default_factory=list, description="Supporting commit hashes")


# ─── Decision Summary ─────────────────────────────────────────────────────────

class DecisionSummarySchema(BaseModel):
    repository_id: str = Field(description="Repository identifier")
    total_decisions: int = Field(description="Total number of decisions discovered")
    total_intents: int = Field(description="Total number of inferred intents")
    by_type: Dict[str, int] = Field(description="Decision count broken down by type")
    by_status: Dict[str, int] = Field(description="Decision count broken down by status")
    average_confidence: float = Field(description="Mean confidence score across all decisions")
    generated_at: str = Field(description="ISO timestamp when this summary was generated")


# ─── Graph View ───────────────────────────────────────────────────────────────

class DecisionGraphNodeSchema(BaseModel):
    id: str
    name: str
    decision_type: str
    status: str
    confidence: float


class DecisionGraphEdgeSchema(BaseModel):
    source: str
    target: str
    relationship_type: str
    confidence: float


class DecisionGraphSchema(BaseModel):
    nodes: List[DecisionGraphNodeSchema] = Field(default_factory=list)
    edges: List[DecisionGraphEdgeSchema] = Field(default_factory=list)


# Resolve forward references
DecisionDetailSchema.model_rebuild()
