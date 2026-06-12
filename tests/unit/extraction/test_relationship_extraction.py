"""Unit tests for the RelationshipExtractor."""

import pytest
from src.domain.enums.language import SupportedLanguage
from src.domain.enums.relationship_type import RelationshipType
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.semantic_evidence_engine.relationship_extractor import RelationshipExtractor
from src.infrastructure.extraction.semantic_evidence_engine.entity_extractor import EntityExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR

def test_relationship_extractor_calls_and_imports():
    source_code = """
import os
def process_data():
    calculate_metrics()
"""
    registry = LanguageRegistry()
    adapter = registry.get_adapter(SupportedLanguage.PYTHON)
    parser = adapter.get_parser()
    tree = parser.parse(bytes(source_code, "utf8"))
    
    ir = EvidenceIR()
    # RelationshipExtractor uses entities for CONTAINS (though none here)
    entity_extractor = EntityExtractor()
    entity_extractor.extract(tree, source_code, "src/main.py", ir)
    
    extractor = RelationshipExtractor()
    extractor.extract(tree, source_code, "src/main.py", ir)
    
    # Check imports
    imports = [r for r in ir.relationships if r.relationship_type == RelationshipType.IMPORTS]
    assert len(imports) == 1
    assert imports[0].target_name == "os"
    
    # Check calls
    calls = [r for r in ir.relationships if r.relationship_type == RelationshipType.CALLS]
    assert len(calls) == 1
    assert calls[0].source_name == "process_data"
    assert calls[0].target_name == "calculate_metrics"
