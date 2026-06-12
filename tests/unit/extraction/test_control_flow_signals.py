"""Unit tests for the ControlFlowExtractor."""

import pytest
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.semantic_evidence_engine.control_flow_extractor import ControlFlowExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR

def test_control_flow_signals():
    source_code = """
def process(x):
    try:
        if x > 0:
            for i in range(x):
                pass
    except ValueError:
        pass
    finally:
        pass
"""
    registry = LanguageRegistry()
    adapter = registry.get_adapter(SupportedLanguage.PYTHON)
    parser = adapter.get_parser()
    tree = parser.parse(bytes(source_code, "utf8"))
    
    ir = EvidenceIR()
    extractor = ControlFlowExtractor()
    extractor.extract(tree, source_code, "src/main.py", ir)
    
    signals = ir.signals
    assert len(signals) >= 5
    
    sig_types = [s.signal_type for s in signals]
    assert "TRY_BLOCK" in sig_types
    assert "CONDITIONAL" in sig_types
    assert "LOOP" in sig_types
    assert "CATCH_BLOCK" in sig_types
    assert "FINALLY_BLOCK" in sig_types
