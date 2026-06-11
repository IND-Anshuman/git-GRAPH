from dataclasses import dataclass, field
from typing import Any, List
from src.infrastructure.extraction.strategies.base import RawEntity, RawRelationship
from src.infrastructure.extraction.semantic_evidence_engine.raw_signal import RawSignal
from src.infrastructure.extraction.semantic_evidence_engine.raw_structure_signature import RawStructureSignature
from src.infrastructure.extraction.semantic_evidence_engine.raw_flow_signature import RawFlowSignature
from src.infrastructure.extraction.semantic_evidence_engine.symbol_graph import SymbolGraph
from src.infrastructure.extraction.semantic_evidence_engine.type_evidence import TypeEvidence
from src.infrastructure.extraction.semantic_evidence_engine.call_site import CallSite
from src.infrastructure.extraction.semantic_evidence_engine.dependency_graph import DependencyNode, DependencyEdge
from src.infrastructure.extraction.semantic_evidence_engine.domain_evidence import ApiEndpointEvidence, EventEvidence, EventSubscriptionEvidence, DatabaseEvidence
from src.infrastructure.extraction.semantic_evidence_engine.compiler_diagnostic import CompilerDiagnostic
from src.infrastructure.extraction.semantic_evidence_engine.provenance import Provenance

@dataclass(frozen=True)
class ExtractionResult:
    entities: List[RawEntity]
    relationships: List[RawRelationship]
    signals: List[RawSignal]
    structure_signatures: List[RawStructureSignature]
    flow_signatures: List[RawFlowSignature]
    symbol_graph: SymbolGraph
    type_evidence: List[TypeEvidence]
    call_sites: List[CallSite]
    dependency_nodes: List[DependencyNode]
    dependency_edges: List[DependencyEdge]
    api_evidence: List[ApiEndpointEvidence]
    event_evidence: List[EventEvidence]
    event_subscriptions: List[EventSubscriptionEvidence]
    database_evidence: List[DatabaseEvidence]
    ai_evidence: List[Any]
    diagnostics: List[CompilerDiagnostic]
    provenance: Provenance
