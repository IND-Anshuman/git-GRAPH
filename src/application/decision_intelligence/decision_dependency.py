from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class DecisionDependency:
    source_decision_id: UUID
    target_decision_id: UUID
    relationship_type: str
    description: str
