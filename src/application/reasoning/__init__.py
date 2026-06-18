"""
Phase 7A — Reasoning Intelligence Layer (RIL): Reasoning Foundations.

Provides purely deterministic, evidence-backed graph reasoning over the
Temporal Code Knowledge Graph.  No LLM calls are made inside this package.

Public surface (consumed by the presentation layer):
    ReasoningQueryEngine  – primary orchestrator
    ReasoningCache        – deterministic result cache
    ReasoningContext      – pipeline carry-bag
    ReasoningResult       – rich, auditable output
"""

from src.application.reasoning.reasoning_question_type import ReasoningQuestionType
from src.application.reasoning.evidence_weight_registry import EvidenceWeightRegistry
from src.application.reasoning.reasoning_confidence import ReasoningConfidence, ConfidenceLevel
from src.application.reasoning.reasoning_evidence import ReasoningEvidence
from src.application.reasoning.evidence_provenance_graph import (
    EvidenceProvenanceGraph,
    ProvenanceNode,
    ProvenanceEdge,
)
from src.application.reasoning.reasoning_limitations import ReasoningLimitation
from src.application.reasoning.reasoning_hypothesis import ReasoningHypothesis
from src.application.reasoning.reasoning_chain import ReasoningChain, ReasoningStep
from src.application.reasoning.reasoning_snapshot import ReasoningSnapshot
from src.application.reasoning.reasoning_context import ReasoningContext
from src.application.reasoning.reasoning_result import ReasoningResult

__all__ = [
    "ReasoningQuestionType",
    "EvidenceWeightRegistry",
    "ReasoningConfidence",
    "ConfidenceLevel",
    "ReasoningEvidence",
    "EvidenceProvenanceGraph",
    "ProvenanceNode",
    "ProvenanceEdge",
    "ReasoningLimitation",
    "ReasoningHypothesis",
    "ReasoningChain",
    "ReasoningStep",
    "ReasoningSnapshot",
    "ReasoningContext",
    "ReasoningResult",
]
