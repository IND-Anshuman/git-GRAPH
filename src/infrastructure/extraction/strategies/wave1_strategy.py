"""Deprecated wave 1 extraction strategy, delegating to the new SEEE engine."""

import warnings
from typing import Any, List, Optional

from src.domain.enums.entity_type import EntityType
from src.domain.enums.relationship_type import RelationshipType
from src.infrastructure.extraction.strategies.base import (
    IExtractionStrategy,
    RawEntity,
    RawRelationship,
)

class Wave1ExtractionStrategy(IExtractionStrategy):
    """Broad structural extractor for first-wave multi-language support.
    
    DEPRECATED: Use SemanticEvidenceExtractionEngine (SEEE) instead.
    """

    def __init__(self, language_key: str) -> None:
        self.language_key = language_key
        self._last_result = None
        warnings.warn(
            "Wave1ExtractionStrategy is deprecated and replaced by SemanticEvidenceExtractionEngine.",
            DeprecationWarning,
            stacklevel=2
        )

    def extract_entities(
        self, tree: Any, source_code: str, file_path: str, module_name: str
    ) -> List[RawEntity]:
        from src.infrastructure.extraction.semantic_evidence_engine.semantic_evidence_engine import SemanticEvidenceExtractionEngine
        engine = SemanticEvidenceExtractionEngine()
        result = engine.extract(tree, source_code, file_path)
        self._last_result = result
        
        # Ensure metadata has language for backward compatibility
        for entity in result.entities:
            if "language" not in entity.metadata:
                entity.metadata["language"] = self.language_key
                
        return result.entities

    def extract_relationships(
        self, tree: Any, source_code: str, entities: List[RawEntity]
    ) -> List[RawRelationship]:
        if self._last_result is not None:
            return self._last_result.relationships
            
        from src.infrastructure.extraction.semantic_evidence_engine.semantic_evidence_engine import SemanticEvidenceExtractionEngine
        engine = SemanticEvidenceExtractionEngine()
        result = engine.extract(tree, source_code, "")
        return result.relationships
