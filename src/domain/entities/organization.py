from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import Any

@dataclass
class OrganizationEntity:
    """Entity representing a corporate organization containing multiple repositories."""
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
