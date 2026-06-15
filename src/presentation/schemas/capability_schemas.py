"""Pydantic API schemas for Phase 6 Capability Intelligence requests and responses."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import uuid

class CapabilityResponse(BaseModel):
    """API response model representing a verified capability."""
    id: uuid.UUID
    repository_id: uuid.UUID
    name: str
    description: Optional[str] = None
    confidence: float
    capability_type: str
    maturity_score: float
    risk_score: float
    coverage_score: float
    concepts: List[str] = Field(default_factory=list)
    behaviors: List[str] = Field(default_factory=list)
    flows: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    relationships: List[str] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True

class CapabilityCandidateResponse(BaseModel):
    """API response model representing a discovered capability candidate."""
    id: uuid.UUID
    repository_id: uuid.UUID
    name: str
    description: Optional[str] = None
    confidence: float
    status: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    capability_type: str
    created_at: datetime

    class Config:
        from_attributes = True

class CapabilityRelationshipResponse(BaseModel):
    """API response model representing a relationship between capabilities."""
    id: uuid.UUID
    repository_id: uuid.UUID
    source_capability_id: uuid.UUID
    target_capability_id: uuid.UUID
    relationship_type: str
    dependency_type: str

    class Config:
        from_attributes = True

class CapabilityQueryRequest(BaseModel):
    """API request model for querying capabilities semantically."""
    query_text: str
    limit: int = 10

class CapabilityQueryResult(BaseModel):
    """API model detail for a semantic query result entry."""
    capability: CapabilityResponse
    relevance_score: float
    matching_evidence: List[str] = Field(default_factory=list)

class CapabilityQueryResponse(BaseModel):
    """API response model for capability queries."""
    results: List[CapabilityQueryResult]

class CapabilityHealthRiskResponse(BaseModel):
    """API response model for capability health, risk, and structural metrics."""
    capability_id: uuid.UUID
    health_score: float
    risk_score: float
    stability_score: float
    cohesion_score: float
    coupling_score: float
    boundary_strength: float
    boundary_leakage_detected: bool

class CapabilityBlastRadiusResponse(BaseModel):
    """API response model representing blast radius and transitive impacts."""
    capability_id: uuid.UUID
    blast_radius_score: float
    impacted_capability_ids: List[uuid.UUID] = Field(default_factory=list)
    impact_depth: int

class TimelineEntry(BaseModel):
    """Timeline entry model for capability drift/evolution."""
    commit_hash: str
    timestamp: datetime
    features: Dict[str, Any]

class CapabilityEvolutionResponse(BaseModel):
    """API response model representing a capability's evolution timeline."""
    capability_id: uuid.UUID
    timeline: List[TimelineEntry] = Field(default_factory=list)
