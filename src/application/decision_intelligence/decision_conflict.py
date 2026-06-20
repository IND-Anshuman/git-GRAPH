from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class DecisionConflict:
    decision_a_id: UUID
    decision_b_id: UUID
    conflict_type: str
    description: str
    detected_at: datetime
    severity: float
