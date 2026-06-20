from dataclasses import dataclass, field
from .decision_snapshot import DecisionSnapshot

@dataclass
class DecisionTimeline:
    repository_id: str
    first_commit: str
    last_commit: str
    snapshots: list[DecisionSnapshot] = field(default_factory=list)
