from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

class RepositoryEventType(str, Enum):
    DEPENDENCY_INTRODUCED = "DEPENDENCY_INTRODUCED"
    DEPENDENCY_REMOVED = "DEPENDENCY_REMOVED"
    SERVICE_CREATED = "SERVICE_CREATED"
    SERVICE_REMOVED = "SERVICE_REMOVED"
    CAPABILITY_CREATED = "CAPABILITY_CREATED"
    CAPABILITY_SPLIT = "CAPABILITY_SPLIT"
    ARCHITECTURE_CHANGED = "ARCHITECTURE_CHANGED"
    OWNERSHIP_CHANGED = "OWNERSHIP_CHANGED"
    MODEL_ADOPTED = "MODEL_ADOPTED"
    FRAMEWORK_ADOPTED = "FRAMEWORK_ADOPTED"

class RepositoryEventSource(str, Enum):
    COMMIT = "COMMIT"
    ADR = "ADR"
    PR = "PR"
    ISSUE = "ISSUE"
    CHANGELOG = "CHANGELOG"
    MANUAL = "MANUAL"

@dataclass(frozen=True)
class RepositoryEvent:
    event_id: UUID
    event_type: RepositoryEventType
    source: RepositoryEventSource
    repository_id: str
    commit_hash: str
    description: str
    occurred_at: datetime
    metadata: dict = field(default_factory=dict)
