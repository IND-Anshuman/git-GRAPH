from dataclasses import dataclass, field
from typing import List
from src.application.semantic.isr.canonical_entity import CanonicalEntity
from src.application.semantic.isr.canonical_relationship import CanonicalRelationship
from src.domain.value_objects.semantic_extraction_report import SemanticExtractionReport
from src.domain.value_objects.intelligence_hints import SemanticHint

@dataclass
class CompilerOutput:
    """Application DTO representing the output of the Semantic Compiler compilation."""
    generated_entities: List[CanonicalEntity] = field(default_factory=list)
    generated_relationships: List[CanonicalRelationship] = field(default_factory=list)
    report: SemanticExtractionReport | None = None
    frameworks_detected: List[str] = field(default_factory=list)
    semantic_hints: List[SemanticHint] = field(default_factory=list)
