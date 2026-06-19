"""Pydantic API schemas for Phase 7B Architectural Intelligence requests and responses."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import uuid
from src.application.architecture.architecture_type import ArchitectureType
from src.application.architecture.architecture_violation import ViolationSeverity
from src.application.architecture.architecture_drift import ArchitectureDriftType
from src.application.architecture.refactoring_candidate import RefactoringCandidateType, RefactoringPriority
from src.application.architecture.architecture_recommendation import RecommendationType

class ArchitectureConfidenceSchema(BaseModel):
    score: float
    topology_match: float
    dependency_match: float
    flow_match: float
    capability_match: float
    ownership_match: float
    historical_match: float
    evidence_coverage: float

    class Config:
        from_attributes = True

class ArchitectureEvidenceSchema(BaseModel):
    capabilities: List[Dict[str, Any]] = Field(default_factory=list)
    flows: List[Dict[str, Any]] = Field(default_factory=list)
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    dependency_paths: List[List[str]] = Field(default_factory=list)
    ownership_paths: List[List[str]] = Field(default_factory=list)
    supporting_patterns: List[str] = Field(default_factory=list)
    violating_patterns: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True

class ArchitectureProfileResponse(BaseModel):
    id: uuid.UUID
    architecture_type: ArchitectureType
    confidence: ArchitectureConfidenceSchema
    description: str
    evidence: ArchitectureEvidenceSchema
    detected_at: datetime
    repository_id: str
    commit_hash: str

    class Config:
        from_attributes = True

class ArchitectureSnapshotResponse(BaseModel):
    snapshot_id: uuid.UUID
    repository_id: str
    commit_hash: str
    architecture_profiles: List[Dict[str, Any]] = Field(default_factory=list)
    fitness_metrics: Dict[str, Any] = Field(default_factory=dict)
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    ownership_profile: Dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime

    class Config:
        from_attributes = True

class ArchitectureFitnessResponse(BaseModel):
    coupling_score: float
    cohesion_score: float
    instability_score: float
    abstractness_score: float
    distance_from_main_sequence: float
    cyclicity_score: float
    layer_violation_score: float
    overall_score: float
    formulas: Dict[str, str] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class ArchitectureViolationResponse(BaseModel):
    id: uuid.UUID
    rule_name: str
    severity: ViolationSeverity
    affected_entities: List[str] = Field(default_factory=list)
    affected_capabilities: List[str] = Field(default_factory=list)
    reason: str
    evidence: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class ArchitectureInvariantResponse(BaseModel):
    name: str
    description: str
    rule_expression: str
    severity: ViolationSeverity
    enabled: bool
    source_role: Optional[str] = None
    forbidden_target_role: Optional[str] = None

    class Config:
        from_attributes = True

class ArchitectureDriftResponse(BaseModel):
    id: uuid.UUID
    drift_type: ArchitectureDriftType
    previous_state: Dict[str, Any] = Field(default_factory=dict)
    current_state: Dict[str, Any] = Field(default_factory=dict)
    delta: Dict[str, Any] = Field(default_factory=dict)
    confidence: float
    from_commit: str
    to_commit: str
    detected_at: datetime

    class Config:
        from_attributes = True

class ArchitectureTimelineEntrySchema(BaseModel):
    commit_hash: str
    architecture_type: ArchitectureType
    key_changes: List[str] = Field(default_factory=list)
    fitness_score: float
    timestamp: datetime

    class Config:
        from_attributes = True

class ArchitectureTimelineResponse(BaseModel):
    id: uuid.UUID
    repository_id: str
    entries: List[ArchitectureTimelineEntrySchema] = Field(default_factory=list)
    generated_at: datetime

    class Config:
        from_attributes = True

class ArchitectureBenchmarkResponse(BaseModel):
    id: uuid.UUID
    repository_id: str
    commit_hash: str
    current_fitness: float
    comparison_group: str
    comparison_avg_fitness: float
    percentile_rank: float
    key_gaps: List[str] = Field(default_factory=list)
    generated_at: datetime

    class Config:
        from_attributes = True

class ArchitectureSimilarityResponse(BaseModel):
    id: uuid.UUID
    source_repository_id: str
    target_repository_id: str
    similarity_score: float
    topology_similarity: float
    dependency_similarity: float
    capability_similarity: float
    flow_similarity: float
    computed_at: datetime

    class Config:
        from_attributes = True

class OwnershipProfileResponse(BaseModel):
    id: uuid.UUID
    repository_id: str
    commit_hash: str
    capability_ownership: Dict[str, List[str]] = Field(default_factory=dict)
    knowledge_silos: List[str] = Field(default_factory=list)
    bus_factor_risks: List[Dict[str, Any]] = Field(default_factory=list)
    unowned_capabilities: List[str] = Field(default_factory=list)
    overloaded_teams: List[Dict[str, Any]] = Field(default_factory=list)
    ownership_drift: List[Dict[str, Any]] = Field(default_factory=list)
    detected_at: datetime
    evidence_sources: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True

class RefactoringCandidateResponse(BaseModel):
    id: uuid.UUID
    candidate_type: RefactoringCandidateType
    priority: RefactoringPriority
    target_entities: List[str] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    expected_benefit: str
    fitness_impact: float
    detected_at: datetime

    class Config:
        from_attributes = True

class ArchitectureRecommendationResponse(BaseModel):
    id: uuid.UUID
    recommendation_type: RecommendationType
    target_elements: List[str] = Field(default_factory=list)
    action_description: str
    justification: str
    expected_fitness_delta: float
    difficulty: str

    class Config:
        from_attributes = True

class ArchitectureNodeSchema(BaseModel):
    node_id: str
    node_type: str
    label: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class ArchitectureEdgeSchema(BaseModel):
    from_id: str
    to_id: str
    relationship: str

    class Config:
        from_attributes = True

class ArchitectureGraphResponse(BaseModel):
    nodes: Dict[str, ArchitectureNodeSchema] = Field(default_factory=dict)
    edges: List[ArchitectureEdgeSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True
