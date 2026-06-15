"""Domain model representing cached capability snapshots."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any

@dataclass
class CapabilitySnapshot:
    """Cached representation of a capability state to optimize GraphRAG queries."""
    id: uuid.UUID
    capability_id: uuid.UUID
    summary: str
    risk: str
    health: Dict[str, Any] = field(default_factory=dict)
    owners: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[Dict[str, Any]] = field(default_factory=list)
    flows: List[str] = field(default_factory=list)
    timeline: List[str] = field(default_factory=list)
    drift: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
