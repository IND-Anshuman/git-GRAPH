"""Unit tests for the ExtractorRegistry."""

import pytest
from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import (
    ExtractorRegistry,
    IBaseExtractor,
)
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR

class MockExtractor(IBaseExtractor):
    def extract(self, tree, source_code, file_path, ir) -> None:
        pass

def test_registry_registration_and_retrieval():
    registry = ExtractorRegistry()
    
    # Register mock extractor
    registry.register(MockExtractor)
    
    # Try duplicate registration
    registry.register(MockExtractor)
    
    extractors = registry.get_extractors()
    assert len(extractors) == 1
    assert isinstance(extractors[0], MockExtractor)
