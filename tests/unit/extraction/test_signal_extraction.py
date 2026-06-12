"""Unit tests for signals populated into EvidenceIR."""

import pytest
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.semantic_evidence_engine.semantic_evidence_engine import SemanticEvidenceExtractionEngine

def test_signal_extraction_populates_signals():
    source_code = """
import fastapi
app = fastapi.FastAPI()

@app.get("/items")
def read_items():
    if True:
        return []
    return None
"""
    registry = LanguageRegistry()
    adapter = registry.get_adapter(SupportedLanguage.PYTHON)
    parser = adapter.get_parser()
    tree = parser.parse(bytes(source_code, "utf8"))
    
    engine = SemanticEvidenceExtractionEngine()
    result = engine.extract(tree, source_code, "src/api.py")
    
    assert len(result.signals) >= 1
    sig_types = {s.signal_type for s in result.signals}
    # Should contain conditional loop control flow
    assert "CONDITIONAL" in sig_types
    # Should contain framework endpoint
    assert "RPC_ENDPOINT" in sig_types
