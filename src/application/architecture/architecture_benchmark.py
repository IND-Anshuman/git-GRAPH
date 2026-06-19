"""Domain model representing architectural benchmarking."""

import uuid
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class ArchitectureBenchmark:
    """Benchmarking metrics comparing the architecture to a group."""
    id: uuid.UUID
    repository_id: str
    commit_hash: str
    current_fitness: float
    comparison_group: str
    comparison_avg_fitness: float
    percentile_rank: float
    key_gaps: list[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
