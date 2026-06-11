from dataclasses import dataclass, field
from typing import Any
from src.domain.value_objects.knowledge_confidence import KnowledgeConfidence

@dataclass(frozen=True)
class RawStructureSignature:
    entity_id: str
    kind: str
    method_count: int
    property_count: int
    dependency_count: int
    inheritance_depth: int
    nested_entity_count: int
    statement_count: int
    cyclomatic_indicators: int
    confidence: KnowledgeConfidence
    generic_parameter_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
