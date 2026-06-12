"""Unit tests for the FlowSignatureExtractor."""

import pytest
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.semantic_evidence_engine.entity_extractor import EntityExtractor
from src.infrastructure.extraction.semantic_evidence_engine.flow_signature_extractor import FlowSignatureExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR

def test_flow_signatures():
    source_code = """
def run_task():
    for x in range(10):
        if x == 5:
            external_func()
"""
    registry = LanguageRegistry()
    adapter = registry.get_adapter(SupportedLanguage.PYTHON)
    parser = adapter.get_parser()
    tree = parser.parse(bytes(source_code, "utf8"))
    
    ir = EvidenceIR()
    # EntityExtractor builds entities first
    entity_extractor = EntityExtractor()
    entity_extractor.extract(tree, source_code, "src/task.py", ir)
    
    extractor = FlowSignatureExtractor()
    extractor.extract(tree, source_code, "src/task.py", ir)
    
    assert len(ir.flow_signatures) == 1
    sig = ir.flow_signatures[0]
    assert sig.entity_id == "run_task"
    assert sig.branch_count >= 1
    assert sig.loop_count >= 1
    assert sig.external_call_count >= 1
