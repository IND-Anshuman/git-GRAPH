"""Domain model representing architectural drift between commits."""

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


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
