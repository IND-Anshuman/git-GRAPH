from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class DecisionVersion:
    decision_id: UUID
    version: int
    commit_hash: str
    confidence: float
    supporting_evidence: list[str] = field(default_factory=list)
    generated_at: datetime = None
