"""Domain model representing similarity between architectures."""

import uuid
from datetime import datetime
from dataclasses import dataclass

@dataclass
class ArchitectureSimilarity:
    """Similarity metrics between two repository architectures."""
    id: uuid.UUID
    source_repository_id: str
    target_repository_id: str
    similarity_score: float
    topology_similarity: float
    dependency_similarity: float
    capability_similarity: float
    flow_similarity: float
    computed_at: datetime
