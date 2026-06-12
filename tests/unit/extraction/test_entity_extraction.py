"""Unit tests for the EntityExtractor."""

import pytest
from src.domain.enums.language import SupportedLanguage
from src.domain.enums.entity_type import EntityType
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.semantic_evidence_engine.entity_extractor import EntityExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR

def test_entity_extractor_class_and_methods():
    source_code = """
class OrderService:
    def __init__(self, repo):
        self.repo = repo
        
    def create_order(self, order_id):
        pass
"""
    registry = LanguageRegistry()
    adapter = registry.get_adapter(SupportedLanguage.PYTHON)
    parser = adapter.get_parser()
    tree = parser.parse(bytes(source_code, "utf8"))
    
    ir = EvidenceIR()
    extractor = EntityExtractor()
    extractor.extract(tree, source_code, "src/order_service.py", ir)
    
    # Check classes
    classes = [e for e in ir.entities if e.entity_type == EntityType.CLASS]
    assert len(classes) == 1
    assert classes[0].name == "OrderService"
    assert classes[0].span.file_path == "src/order_service.py"
    
    # Check functions/methods (Python AST parses methods as function_definition)
    funcs = [e for e in ir.entities if e.entity_type == EntityType.FUNCTION]
    assert len(funcs) == 2
    func_names = {f.name for f in funcs}
    assert "__init__" in func_names
    assert "create_order" in func_names
