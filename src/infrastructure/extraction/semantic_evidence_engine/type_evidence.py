from dataclasses import dataclass
from src.domain.value_objects.knowledge_confidence import KnowledgeConfidence

@dataclass(frozen=True)
class TypeEvidence:
    symbol_id: str
    inferred_type: str
    source: str
    confidence: KnowledgeConfidence
