from dataclasses import dataclass, field
from typing import Any
import uuid

from src.domain.enums.mutation_type import MutationType
from src.domain.value_objects.entity_id import SEID

@dataclass
class EntityVersion:
    """Entity representing a specific version of a CodeEntity at a given commit."""
    id: uuid.UUID
    seid: SEID
    commit_hash: str
    version_ordinal: int
    mutation_type: MutationType
    canonical_name: str
    file_path: str
    start_line: int
    end_line: int
    content_hash: str
    structural_fingerprint: str
    confidence: float = 1.0
    source_text: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
