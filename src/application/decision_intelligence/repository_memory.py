from dataclasses import dataclass, field
from .repository_event import RepositoryEvent

@dataclass
class RepositoryMemory:
    repository_id: str
    events: list[RepositoryEvent] = field(default_factory=list)
    technology_introductions: list[str] = field(default_factory=list)
    service_creations: list[str] = field(default_factory=list)
    capability_changes: list[str] = field(default_factory=list)
    architecture_changes: list[str] = field(default_factory=list)
    ownership_changes: list[str] = field(default_factory=list)
