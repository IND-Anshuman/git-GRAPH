from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

@dataclass
class MemoryArtifact:
    artifact_id: UUID
    repository_id: str
    artifact_type: str
    content: dict
    source_event_id: UUID
    created_at: datetime
