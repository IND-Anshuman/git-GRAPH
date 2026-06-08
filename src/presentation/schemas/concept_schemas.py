"""Pydantic API schemas for Phase 4 Concept Graph and Intelligence requests and responses."""

from datetime import datetime
from typing import Dict, List, Optional
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
