"""Domain model representing the architecture evolution timeline."""

import uuid
from datetime import datetime
from dataclasses import dataclass, field

from .architecture_type import ArchitectureType

@dataclass
class ArchitectureTimelineEntry:
    """A single entry in the architecture timeline."""
    commit_hash: str
    architecture_type: ArchitectureType
    key_changes: list[str] = field(default_factory=list)
    fitness_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ArchitectureTimeline:
    """The complete sequence of architectural state over time."""
    id: uuid.UUID
    repository_id: str
    entries: list[ArchitectureTimelineEntry] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
