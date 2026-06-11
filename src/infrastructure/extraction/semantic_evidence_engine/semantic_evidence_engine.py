"""Semantic Evidence Extraction Engine (SEEE) orchestrator."""

from datetime import datetime
from typing import Any

from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import ExtractorRegistry
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR
from src.infrastructure.extraction.semantic_evidence_engine.extraction_result import ExtractionResult
from src.infrastructure.extraction.semantic_evidence_engine.provenance import Provenance

# Import all 12 extractors
from src.infrastructure.extraction.semantic_evidence_engine.entity_extractor import EntityExtractor
from src.infrastructure.extraction.semantic_evidence_engine.relationship_extractor import RelationshipExtractor
from src.infrastructure.extraction.semantic_evidence_engine.scope_extractor import ScopeExtractor
from src.infrastructure.extraction.semantic_evidence_engine.symbol_resolution_extractor import SymbolResolutionExtractor
from src.infrastructure.extraction.semantic_evidence_engine.control_flow_extractor import ControlFlowExtractor
from src.infrastructure.extraction.semantic_evidence_engine.data_flow_extractor import DataFlowExtractor
from src.infrastructure.extraction.semantic_evidence_engine.framework_signal_extractor import FrameworkSignalExtractor
from src.infrastructure.extraction.semantic_evidence_engine.structure_signature_extractor import StructureSignatureExtractor
from src.infrastructure.extraction.semantic_evidence_engine.flow_signature_extractor import FlowSignatureExtractor
from src.infrastructure.extraction.semantic_evidence_engine.ai_signal_extractor import AISignalExtractor
from src.infrastructure.extraction.semantic_evidence_engine.frontend_signal_extractor import FrontendSignalExtractor
from src.infrastructure.extraction.semantic_evidence_engine.diagnostic_collector import DiagnosticCollector

class SemanticEvidenceExtractionEngine:
    """The next-generation extraction subsystem that replaces Wave1ExtractionStrategy."""

    def __init__(self) -> None:
        self.registry = ExtractorRegistry()
        
        # Register all 12 extractors in logical pipeline order
        self.registry.register(EntityExtractor)
        self.registry.register(RelationshipExtractor)
        self.registry.register(ScopeExtractor)
        self.registry.register(SymbolResolutionExtractor)
        self.registry.register(ControlFlowExtractor)
        self.registry.register(DataFlowExtractor)
        self.registry.register(FrameworkSignalExtractor)
        self.registry.register(StructureSignatureExtractor)
        self.registry.register(FlowSignatureExtractor)
        self.registry.register(AISignalExtractor)
        self.registry.register(FrontendSignalExtractor)
        self.registry.register(DiagnosticCollector)

    def extract(self, tree: Any, source_code: str, file_path: str) -> ExtractionResult:
        """Run all registered extractors sequentially on the tree and return the ExtractionResult."""
        provenance = Provenance(
            extractor="SemanticEvidenceExtractionEngine",
            extraction_version="2.0.0",
            extraction_timestamp=datetime.utcnow()
        )
        
        ir = EvidenceIR(provenance=provenance)
        
        # Execute each extractor sequentially
        for extractor in self.registry.get_extractors():
            extractor.extract(tree, source_code, file_path, ir)
            
        return ExtractionResult(
            entities=ir.entities,
            relationships=ir.relationships,
            signals=ir.signals,
            structure_signatures=ir.structure_signatures,
            flow_signatures=ir.flow_signatures,
            symbol_graph=ir.symbol_graph,
            type_evidence=ir.type_evidence,
            call_sites=ir.call_sites,
            dependency_nodes=ir.dependency_nodes,
            dependency_edges=ir.dependency_edges,
            api_evidence=ir.api_evidence,
            event_evidence=ir.event_evidence,
            event_subscriptions=ir.event_subscriptions,
            database_evidence=ir.database_evidence,
            ai_evidence=ir.ai_evidence,
            diagnostics=ir.diagnostics,
            provenance=provenance
        )
