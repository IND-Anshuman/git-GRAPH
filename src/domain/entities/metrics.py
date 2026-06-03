from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class AccuracyReport:
    """Domain entity representing evaluated accuracy metrics against ground truth."""
    id: uuid.UUID
    repository_id: uuid.UUID
    commit_hash: str
    rename_precision: float
    rename_recall: float
    move_precision: float
    move_recall: float
    event_accuracy: float
    reconstruction_accuracy: float
    measured_at: datetime

@dataclass
class BenchmarkReport:
    """Domain entity representing a performance benchmark scan audit."""
    id: uuid.UUID
    repository_id: uuid.UUID
    commit_hash: str
    scan_duration_ms: int
    diff_throughput_nodes_sec: float
    reconstruction_latency_ms: int
    db_size_bytes: int
    memory_rss_bytes: int
    measured_at: datetime
