from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from typing import Any

@dataclass(frozen=True)
class DecisionSnapshot:
    snapshot_id: UUID
    repository_id: str
    commit_hash: str
    decision_ids: list[str] = field(default_factory=list)
    generated_at: datetime = None
