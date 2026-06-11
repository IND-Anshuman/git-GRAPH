from dataclasses import dataclass, field
from typing import Any
from src.domain.value_objects.knowledge_confidence import KnowledgeConfidence

@dataclass(frozen=True)
class RawFlowSignature:
    entity_id: str
    node_count: int
    branch_count: int
    loop_count: int
    async_boundary_count: int
    external_call_count: int
    confidence: KnowledgeConfidence
    metadata: dict[str, Any] = field(default_factory=dict)
