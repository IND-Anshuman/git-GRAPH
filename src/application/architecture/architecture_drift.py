"""Domain model representing architectural drift between commits."""

import uuid
from enum import Enum
from datetime import datetime
from dataclasses import dataclass

class ArchitectureDriftType(str, Enum):
    """Types of architectural drift."""
    DEPENDENCY_DRIFT = "DEPENDENCY_DRIFT"
    FLOW_DRIFT = "FLOW_DRIFT"
    CAPABILITY_DRIFT = "CAPABILITY_DRIFT"
    OWNERSHIP_DRIFT = "OWNERSHIP_DRIFT"
    TOPOLOGY_DRIFT = "TOPOLOGY_DRIFT"
    STYLE_DRIFT = "STYLE_DRIFT"

@dataclass
class ArchitectureDrift:
    """Detected architectural drift between two states."""
    id: uuid.UUID
    drift_type: ArchitectureDriftType
    previous_state: dict
    current_state: dict
    delta: dict
    confidence: float
    from_commit: str
    to_commit: str
    detected_at: datetime
