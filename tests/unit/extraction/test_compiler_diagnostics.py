"""Unit tests for the DiagnosticCollector."""

import pytest
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.semantic_evidence_engine.diagnostic_collector import DiagnosticCollector
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR

def test_compiler_diagnostics_syntax_error():
    # Invalid Python syntax: missing colon and unclosed parentheses
    source_code = """
def invalid_syntax(x
    if x > 0
        return True
"""
    registry = LanguageRegistry()
    adapter = registry.get_adapter(SupportedLanguage.PYTHON)
    parser = adapter.get_parser()
    tree = parser.parse(bytes(source_code, "utf8"))
    
    ir = EvidenceIR()
    extractor = DiagnosticCollector()
    extractor.extract(tree, source_code, "src/invalid.py", ir)
    
    # Check that a syntax error was collected
    assert len(ir.diagnostics) >= 1
    diag = ir.diagnostics[0]
    assert diag.severity == "ERROR"
    assert diag.category == "PARSING"
    assert diag.code == "SYNTAX_ERROR"
    assert "Syntax error" in diag.message
