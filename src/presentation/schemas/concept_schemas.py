"""Pydantic API schemas for Phase 4 Concept Graph and Intelligence requests and responses."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ConceptResponse(BaseModel):
    """API response model representing a single detected concept node."""

    id: str
    ontology_node_id: str
    name: str
    confidence: float
    is_active: bool
    created_at: datetime


class EvolutionTransition(BaseModel):
    """API model detail representing a chronological transition step."""

    type: str
    similarity_score: float


class ConceptEvolutionResponse(BaseModel):
    """API response model for a concept evolution timeline version."""

    concept_version_id: str
    commit_hash: str
    version_number: int
    confidence: float
    transition: Optional[EvolutionTransition] = None


class ConceptDriftResponse(BaseModel):
    """API response model for multi-dimensional drift details."""

    concept_id: str
    drift_score: float
    drift_category: str
    dimension_scores: Dict[str, float]


class ConceptMapNode(BaseModel):
    """API model detail for a concept map node."""

    id: str
    label: str
    type: str = "Concept"


class ConceptMapEdge(BaseModel):
    """API model detail for a concept map edge."""

    from_: str = Field(..., alias="from")
    to: str
    type: str
    confidence: float

    class Config:
        populate_by_name = True


class ConceptMapResponse(BaseModel):
    """API response model for a full repository concept map."""

    nodes: List[ConceptMapNode]
    edges: List[ConceptMapEdge]


class ConceptExplanationResponse(BaseModel):
    """API response model representing a structured breakdown explanation."""

    id: str
    concept_version_id: str
    summary: str
    detail: dict


class BackfillResponse(BaseModel):
    """API response model for backfill triggering status."""

    status: str
    processed_commits: int


class FrameworkDefinitionResponse(BaseModel):
    """API response model representing a framework definition."""

    id: str
    framework_name: str
    language: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class FrameworkVersionResponse(BaseModel):
    """API response model representing a framework version registry entry."""

    id: str
    framework_id: str
    version_string: str
    supported_syntax_rules: Dict[str, Any] = Field(default_factory=dict)
    released_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BehaviorFamilyResponse(BaseModel):
    """API response model representing a behavior family."""

    id: str
    name: str
    parent_concept_id: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class CanonicalBehaviorResponse(BaseModel):
    """API response model representing a canonical behavior."""

    id: str
    name: str
    family_id: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BehaviorAliasResponse(BaseModel):
    """API response model representing a language-specific behavior alias mapping."""

    id: str
    canonical_behavior_id: str
    language: str
    imports: List[str]
    calls: List[str]
    heuristics: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class CanonicalFlowResponse(BaseModel):
    """API response model representing a traced canonical flow."""

    id: str
    flow_type: str
    source_entity_id: str
    target_entity_id: str
    intermediate_entities: List[str]
    confidence: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    class Config:
        from_attributes = True

