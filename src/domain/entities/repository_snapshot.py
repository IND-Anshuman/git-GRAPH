from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid

from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId

@dataclass
class RepositorySnapshot:
    """Entity representing a materialized snapshot checkpoint of the repository's code entities at a specific commit."""
    id: uuid.UUID
    repository_id: RepositoryId
    commit_hash: str
    entity_seids: list[SEID]
    snapshot_data: dict[str, Any]
    created_at: datetime
