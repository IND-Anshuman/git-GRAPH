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

@dataclass
class EvidenceIR:
    entities: List[RawEntity] = field(default_factory=list)
    relationships: List[RawRelationship] = field(default_factory=list)
    signals: List[RawSignal] = field(default_factory=list)
    structure_signatures: List[RawStructureSignature] = field(default_factory=list)
    flow_signatures: List[RawFlowSignature] = field(default_factory=list)
    symbol_graph: SymbolGraph = field(default_factory=SymbolGraph)
    type_evidence: List[TypeEvidence] = field(default_factory=list)
    call_sites: List[CallSite] = field(default_factory=list)
    dependency_nodes: List[DependencyNode] = field(default_factory=list)
    dependency_edges: List[DependencyEdge] = field(default_factory=list)
    api_evidence: List[ApiEndpointEvidence] = field(default_factory=list)
    event_evidence: List[EventEvidence] = field(default_factory=list)
    event_subscriptions: List[EventSubscriptionEvidence] = field(default_factory=list)
    database_evidence: List[DatabaseEvidence] = field(default_factory=list)
    ai_evidence: List[Any] = field(default_factory=list)
    diagnostics: List[CompilerDiagnostic] = field(default_factory=list)
    provenance: Provenance | None = None
