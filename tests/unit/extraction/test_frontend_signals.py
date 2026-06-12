"""Unit tests for the FrontendSignalExtractor."""

import pytest
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.semantic_evidence_engine.entity_extractor import EntityExtractor
from src.infrastructure.extraction.semantic_evidence_engine.frontend_signal_extractor import FrontendSignalExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR

def test_frontend_signals():
    source_code = """
class UserProfileComponent:
    def useThemeHook(self):
        pass
        
def useUserQuery():
    pass
"""
    registry = LanguageRegistry()
    adapter = registry.get_adapter(SupportedLanguage.PYTHON)
    parser = adapter.get_parser()
    tree = parser.parse(bytes(source_code, "utf8"))
    
    ir = EvidenceIR()
    # EntityExtractor builds entities first
    entity_extractor = EntityExtractor()
    entity_extractor.extract(tree, source_code, "src/Component.py", ir)
    
    extractor = FrontendSignalExtractor()
    extractor.extract(tree, source_code, "src/Component.py", ir)
    
    signals = ir.signals
    sig_types = [s.signal_type for s in signals]
    
    assert "COMPONENT_DECLARATION" in sig_types
    assert "QUERY_HOOK" in sig_types
