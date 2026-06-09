"""API Schemas for Phase 4.75 Meta-Ontology expansion request and response models."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MetaTypeSchema(BaseModel):
    id: str
    name: str
    category: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MetaDefinitionSchema(BaseModel):
    id: uuid.UUID
    type_id: str
    major_version: int
    minor_version: int
    patch_version: int
    schema_definition: Dict[str, Any]
    semantic_signature: Dict[str, Any]
    created_at: datetime
    version_string: str

    class Config:
        from_attributes = True


class EmbeddingModelSchema(BaseModel):
    id: str
    model_name: str
    provider: str
    dimensions: int
    distance_metric: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EmbeddingVersionSchema(BaseModel):
    id: uuid.UUID
    model_id: str
    version_string: str
    configuration: Dict[str, Any]
    registered_at: datetime

    class Config:
        from_attributes = True


class RegisterModelRequest(BaseModel):
    id: str = Field(..., description="Unique model key, e.g., 'text-embedding-3-small'")
    model_name: str
    provider: str
    dimensions: int
    distance_metric: str
    is_active: bool = False


class RegisterVersionRequest(BaseModel):
    version_string: str = Field(..., description="Semantic version of model configuration")
    configuration: Dict[str, Any] = Field(default_factory=dict)


class RegisterTypeRequest(BaseModel):
    id: str = Field(..., description="Unique type identifier, e.g., 'Saga'")
    name: str
    category: str = Field(..., description="Category, e.g. STRUCTURAL, BEHAVIORAL")
    status: str = "EXPERIMENTAL"


class RegisterDefinitionRequest(BaseModel):
    schema_definition: Dict[str, Any]
    semantic_signature: Dict[str, Any] = Field(default_factory=dict)
    version_string: str = "1.0.0"


class DiscoveredCandidateSchema(BaseModel):
    meta_type: MetaTypeSchema
    definition: MetaDefinitionSchema


class DiscoveryResponse(BaseModel):
    candidates: List[DiscoveredCandidateSchema]


class PromotionApprovalRequest(BaseModel):
    approver: str = Field(..., description="Name of the person/role approving this promotion")


class ConceptCandidateEvidenceSchema(BaseModel):
    supporting_entities: List[str] = Field(default_factory=list)
    supporting_relationships: List[str] = Field(default_factory=list)
    supporting_behaviors: List[str] = Field(default_factory=list)
    supporting_flows: List[str] = Field(default_factory=list)
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict)


class ConceptCandidateSchema(BaseModel):
    id: uuid.UUID
    name: str
    confidence: float
    evidence: ConceptCandidateEvidenceSchema
    ontology_parent_candidate: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class CanonicalFlowSchema(BaseModel):
    id: str
    flow_type: str
    source_entity_id: str
    target_entity_id: str
    intermediate_entities: List[str] = Field(default_factory=list)
    confidence: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class EvolutionDiffSchema(BaseModel):
    added_entities: List[Dict[str, Any]] = Field(default_factory=list)
    removed_entities: List[Dict[str, Any]] = Field(default_factory=list)
    added_relationships: List[Dict[str, Any]] = Field(default_factory=list)
    removed_relationships: List[Dict[str, Any]] = Field(default_factory=list)
    added_behaviors: List[Dict[str, Any]] = Field(default_factory=list)
    removed_behaviors: List[Dict[str, Any]] = Field(default_factory=list)
    added_concepts: List[Dict[str, Any]] = Field(default_factory=list)
    removed_concepts: List[Dict[str, Any]] = Field(default_factory=list)
