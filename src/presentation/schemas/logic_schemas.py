"""API Schemas for Phase 3 Behavioral Intelligence request and response models."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class OntologyNodeSchema(BaseModel):
    id: str
    name: str
    parent_id: Optional[str]
    domain: str
    description: str
    ontology_version: str
    is_leaf: bool
    metadata: Dict[str, Any]
    loaded_at: datetime


class BehaviorPatternSchema(BaseModel):
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


class LogicSignatureSchema(BaseModel):
    id: str
    repository_id: str
    canonical_name: str
    language: str
    ontology_node_id: Optional[str]
    description: str
    created_at: datetime
    metadata: Dict[str, Any]


class LogicFingerprintSchema(BaseModel):
    structure_hash: str
    dependency_hash: str
    behavioral_hash: str
    composite: str


class ConfidenceBreakdownSchema(BaseModel):
    overall_confidence: float
    ast_confidence: float
    dependency_confidence: float
    data_flow_confidence: float
    pattern_confidence: float
    structural_confidence: float
    evidence_count: int


class LogicVersionSchema(BaseModel):
    id: str
    logic_signature_id: str
    code_entity_seid: str
    commit_hash: str
    version_ordinal: int
    fingerprint: LogicFingerprintSchema
    overall_confidence: float
    confidence_breakdown: Optional[ConfidenceBreakdownSchema]
    is_primary: bool
    metadata: Dict[str, Any]
    created_at: datetime


class LogicEvidenceSchema(BaseModel):
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


class LogicTransitionSchema(BaseModel):
    id: str
    from_logic_version_id: Optional[str]
    to_logic_version_id: Optional[str]
    transition_type: str
    similarity_score: float
    overall_confidence: float
    metadata: Dict[str, Any]
    created_at: datetime


class RuleVerdictSchema(BaseModel):
    rule_id: str
    rule_description: str
    passed: bool
    contribution: float
    evidence_ref: Optional[str]


class BehaviorExplanationSchema(BaseModel):
    id: str
    logic_version_id: str
    behavior_name: str
    ontology_path: str
    overall_confidence: float
    confidence_breakdown: ConfidenceBreakdownSchema
    matched_pattern_ids: List[str]
    evidence_summary: str
    rule_verdicts: List[RuleVerdictSchema]
    is_stale: bool
    generated_at: datetime
    metadata: Dict[str, Any]


class DriftDimensionsSchema(BaseModel):
    structural_drift: float
    dependency_drift: float
    api_surface_drift: float
    control_flow_drift: float
    ontology_drift: float
    security_drift: float


class BehaviorDriftSchema(BaseModel):
    id: str
    logic_transition_id: str
    from_logic_version_id: str
    to_logic_version_id: str
    drift_score: float
    drift_category: str
    dimension_scores: DriftDimensionsSchema
    ontology_changed: bool
    security_boundary_crossed: bool
    computed_at: datetime
    metadata: Dict[str, Any]


class LogicClusterSchema(BaseModel):
    id: str
    name: str
    category: str
    logic_signature_ids: List[str]
    metadata: Dict[str, Any]


class BehaviorEvolutionGraphSchema(BaseModel):
    versions: List[LogicVersionSchema]
    transitions: List[LogicTransitionSchema]


class ValidationIssueSchema(BaseModel):
    issue_type: str
    severity: str
    description: str
    target_id: str


class LogicValidationReportSchema(BaseModel):
    is_valid: bool
    issues: List[ValidationIssueSchema]
