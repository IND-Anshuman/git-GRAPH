"""Unit tests for the DataFlowExtractor."""

import pytest
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.semantic_evidence_engine.data_flow_extractor import DataFlowExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR

def test_data_flow_signals():
    source_code = """
def update_user(user_id, data):
    import json
    payload = json.dumps(data)
    db.session.execute("UPDATE users SET val = 1")
    return True
"""
    registry = LanguageRegistry()
    adapter = registry.get_adapter(SupportedLanguage.PYTHON)
    parser = adapter.get_parser()
    tree = parser.parse(bytes(source_code, "utf8"))
    
    ir = EvidenceIR()
    extractor = DataFlowExtractor()
    extractor.extract(tree, source_code, "src/main.py", ir)
    
    signals = ir.signals
    sig_types = [s.signal_type for s in signals]
    
    # Should have parameter flow for user_id and data
    assert "PARAMETER_FLOW" in sig_types
    # Should have serialization (json.dumps)
    assert "SERIALIZATION" in sig_types
    # Should have database query
    assert "DATABASE_QUERY" in sig_types
    # Should have return flow
    assert "RETURN_FLOW" in sig_types
    
    assert len(ir.database_evidence) == 1
    assert ir.database_evidence[0].operation == "EXECUTE"
