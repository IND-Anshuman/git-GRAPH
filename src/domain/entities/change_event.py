from dataclasses import dataclass, field
from typing import Any
import uuid

from src.domain.enums.mutation_type import MutationType
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId

@dataclass
class ChangeEvent:
    """Entity representing a specific change event occurring on a CodeEntity at a commit."""
    id: uuid.UUID
    repository_id: RepositoryId
    commit_hash: str
    seid: SEID
    change_type: MutationType
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
