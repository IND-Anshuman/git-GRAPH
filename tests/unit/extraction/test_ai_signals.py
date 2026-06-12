"""Unit tests for the AISignalExtractor."""

import pytest
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.semantic_evidence_engine.entity_extractor import EntityExtractor
from src.infrastructure.extraction.semantic_evidence_engine.ai_signal_extractor import AISignalExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR

def test_ai_signals():
    source_code = """
class OrderAgent:
    def execute_prompt(self):
        openai.ChatCompletion.create(model="gpt-4")
        memory.save(key="val")
        
def search_tool():
    pass
"""
    registry = LanguageRegistry()
    adapter = registry.get_adapter(SupportedLanguage.PYTHON)
    parser = adapter.get_parser()
    tree = parser.parse(bytes(source_code, "utf8"))
    
    ir = EvidenceIR()
    # EntityExtractor builds entities first
    entity_extractor = EntityExtractor()
    entity_extractor.extract(tree, source_code, "src/agent.py", ir)
    
    extractor = AISignalExtractor()
    extractor.extract(tree, source_code, "src/agent.py", ir)
    
    signals = ir.signals
    sig_types = [s.signal_type for s in signals]
    
    assert "AGENT_DECLARATION" in sig_types
    assert "TOOL_DECLARATION" in sig_types
    assert "MODEL_USAGE" in sig_types
    assert "MEMORY_ACCESS" in sig_types
