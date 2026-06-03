from dataclasses import dataclass, field
from typing import Any
import uuid

from src.domain.enums.mutation_type import MutationType

@dataclass
class RelationshipVersion:
    """Entity representing a specific versioned change to a Relationship at a given commit."""
    id: uuid.UUID
    relationship_id: uuid.UUID
    commit_hash: str
    mutation_type: MutationType
    version_ordinal: int
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
