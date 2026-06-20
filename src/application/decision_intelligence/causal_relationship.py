from dataclasses import dataclass, field
from uuid import UUID

@dataclass(frozen=True)
class CausalRelationship:
    cause_id: UUID
    effect_id: UUID
    cause_label: str
    effect_label: str
    relationship_type: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
