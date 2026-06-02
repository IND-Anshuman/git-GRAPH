from dataclasses import dataclass, field
from typing import Any
import uuid

from src.domain.entities.entity_version import EntityVersion
from src.domain.entities.relationship_version import RelationshipVersion
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId

@dataclass
class TemporalGraph:
    """Domain model representing a Repository's history of entities and relationships."""
    repository_id: RepositoryId
    entities: dict[SEID, list[EntityVersion]] = field(default_factory=dict)
    relationships: dict[uuid.UUID, list[RelationshipVersion]] = field(default_factory=dict)
