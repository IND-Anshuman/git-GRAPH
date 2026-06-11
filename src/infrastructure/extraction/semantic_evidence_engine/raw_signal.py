from dataclasses import dataclass, field
from typing import Any
from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan
from src.domain.value_objects.knowledge_confidence import KnowledgeConfidence

@dataclass(frozen=True)
class RawSignal:
    id: str
    signal_type: str
    value: str | None
    confidence: KnowledgeConfidence
    source_entity_id: str | None
    span: SourceSpan
    metadata: dict[str, Any] = field(default_factory=dict)
