"""Unit tests for the StructureSignatureExtractor."""

import pytest
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.semantic_evidence_engine.entity_extractor import EntityExtractor
from src.infrastructure.extraction.semantic_evidence_engine.structure_signature_extractor import StructureSignatureExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR

def test_structure_signatures():
    source_code = """
class DataManager:
    def __init__(self):
        self.value = 1
        
    def save(self):
        if self.value > 0:
            return True
        return False
"""
    registry = LanguageRegistry()
    adapter = registry.get_adapter(SupportedLanguage.PYTHON)
    parser = adapter.get_parser()
    tree = parser.parse(bytes(source_code, "utf8"))
    
    ir = EvidenceIR()
    # EntityExtractor builds entities first
    entity_extractor = EntityExtractor()
    entity_extractor.extract(tree, source_code, "src/manager.py", ir)
    
    extractor = StructureSignatureExtractor()
    extractor.extract(tree, source_code, "src/manager.py", ir)
    
    # We should have structure signatures for all entities (Class and Functions)
    assert len(ir.structure_signatures) == 3
    
    # Check the DataManager class structure signature
    class_sig = next(s for s in ir.structure_signatures if s.entity_id == "DataManager")
    assert class_sig.kind == "CLASS"
    
    # The count_metrics counts method/function definitions inside the class node
    assert class_sig.method_count == 2
    assert class_sig.nested_entity_count == 0
