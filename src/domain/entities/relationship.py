from dataclasses import dataclass, field
from typing import Any
import uuid

from src.domain.enums.relationship_type import RelationshipType
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.exceptions import InvalidEntityException

@dataclass
class Relationship:
    """Entity representing a directed relationship between two code entities."""
    id: uuid.UUID
    repository_id: RepositoryId
    relationship_type: RelationshipType
    source_seid: SEID
    target_seid: SEID
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate relationship constraints."""
        if self.source_seid == self.target_seid and self.relationship_type != RelationshipType.BELONGS_TO:
            raise InvalidEntityException("Source and target SEID cannot be the same for non-BELONGS_TO relationships")
