"""Pydantic DTO models for Phase 3 Behavioral Intelligence responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class OntologyNodeResponse(BaseModel):
    """DTO for an OntologyNode."""

    id: str
    name: str
    parent_id: Optional[str]
    domain: str
    description: str
    ontology_version: str
    is_leaf: bool
    metadata: Dict[str, Any]
    loaded_at: datetime


class BehaviorPatternResponse(BaseModel):
    """DTO for a BehaviorPattern."""

    id: str
    pattern_id: str
    name: str
    ontology_node_id: str
    base_confidence: float
    pattern_version: str
    schema_version: str
    rules: Dict[str, Any]
    index_keys: List[str]
    is_active: bool
    loaded_at: datetime


class LogicSignatureResponse(BaseModel):
    """DTO for a LogicSignature."""

    id: str
    repository_id: str
    canonical_name: str
    language: str
    ontology_node_id: Optional[str]
    description: str
    created_at: datetime
    metadata: Dict[str, Any]


class LogicFingerprintResponse(BaseModel):
    """DTO for a LogicFingerprint."""

    structure_hash: str
    dependency_hash: str
    behavioral_hash: str
    composite: str


class ConfidenceBreakdownResponse(BaseModel):
    """DTO for a ConfidenceBreakdown."""

    overall_confidence: float
    ast_confidence: float
    dependency_confidence: float
    data_flow_confidence: float
    pattern_confidence: float
    structural_confidence: float
    evidence_count: int


class LogicVersionResponse(BaseModel):
    """DTO for a LogicVersion."""

    id: str
    logic_signature_id: str
    code_entity_seid: str
    commit_hash: str
    version_ordinal: int
    fingerprint: LogicFingerprintResponse
    overall_confidence: float
    confidence_breakdown: Optional[ConfidenceBreakdownResponse]
    is_primary: bool
    metadata: Dict[str, Any]
    created_at: datetime


class LogicEvidenceResponse(BaseModel):
    """DTO for a LogicEvidence."""

    id: str
    logic_version_id: str
    evidence_type: str
    file_path: str
    start_line: int
    end_line: int
    ast_node_type: Optional[str]
    matched_symbol: Optional[str]
    matched_rule_id: Optional[str]
    call_chain: List[str]
    data_flow_path: Optional[List[str]]
    confidence_contribution: float
    metadata: Dict[str, Any]
    detected_at: datetime


class LogicTransitionResponse(BaseModel):
    """DTO for a LogicTransition."""

    id: str
    from_logic_version_id: Optional[str]
    to_logic_version_id: Optional[str]
    transition_type: str
    similarity_score: float
    overall_confidence: float
    metadata: Dict[str, Any]
    created_at: datetime


class RuleVerdictResponse(BaseModel):
    """DTO for a single rule verdict within an explanation."""

    rule_id: str
    rule_description: str
    passed: bool
    contribution: float
    evidence_ref: Optional[str]


class BehaviorExplanationResponse(BaseModel):
    """DTO for a BehaviorExplanation."""

    id: str
    logic_version_id: str
    behavior_name: str
    ontology_path: str
    overall_confidence: float
    confidence_breakdown: ConfidenceBreakdownResponse
    matched_pattern_ids: List[str]
    evidence_summary: str
    rule_verdicts: List[RuleVerdictResponse]
    is_stale: bool
    generated_at: datetime
    metadata: Dict[str, Any]


class DriftDimensionsResponse(BaseModel):
    """DTO for DriftDimensions."""

    structural_drift: float
    dependency_drift: float
    api_surface_drift: float
    control_flow_drift: float
    ontology_drift: float
    security_drift: float


class BehaviorDriftResponse(BaseModel):
    """DTO for a BehaviorDrift."""

    id: str
    logic_transition_id: str
    from_logic_version_id: str
    to_logic_version_id: str
    drift_score: float
    drift_category: str
    dimension_scores: DriftDimensionsResponse
    ontology_changed: bool
    security_boundary_crossed: bool
    computed_at: datetime
    metadata: Dict[str, Any]


class LogicClusterResponse(BaseModel):
    """DTO for a LogicCluster."""

    id: str
    name: str
    category: str
    logic_signature_ids: List[str]
    metadata: Dict[str, Any]
