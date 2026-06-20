from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

@dataclass
class DecisionImpactEntry:
    commit_hash: str
    description: str
    timestamp: datetime

@dataclass
class DecisionImpactTimeline:
    decision_id: UUID
    entries: list[DecisionImpactEntry] = field(default_factory=list)
