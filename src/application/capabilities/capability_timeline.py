"""Domain model representing capability timeline history."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class CapabilityTimeline:
    """Chronological checkpoint mapping which features/modules are active for a capability at a specific commit."""
    id: str
    capability_id: str
    commit_hash: str
    features: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
