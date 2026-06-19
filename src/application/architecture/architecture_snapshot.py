"""Domain model representing an architecture snapshot in time."""

import uuid
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class ArchitectureSnapshot:
    """Architectural equivalent of CapabilitySnapshot to avoid recomputing old states."""
    snapshot_id: uuid.UUID
    repository_id: str
    commit_hash: str
    architecture_profiles: list[dict] = field(default_factory=list)
    fitness_metrics: dict = field(default_factory=dict)
    violations: list[dict] = field(default_factory=list)
    ownership_profile: dict = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)
