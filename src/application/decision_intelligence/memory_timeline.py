from dataclasses import dataclass, field
from datetime import datetime
from .memory_artifact import MemoryArtifact

@dataclass
class MemoryTimeline:
    repository_id: str
    first_event_at: datetime
    last_event_at: datetime
    artifacts: list[MemoryArtifact] = field(default_factory=list)
