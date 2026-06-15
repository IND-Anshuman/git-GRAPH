"""Domain models representing relationships and dependencies between capabilities."""

import uuid
from dataclasses import dataclass
from enum import Enum

class CapabilityDependencyType(str, Enum):
    """Specific technical mechanism of capability interaction."""
    DATA = "DATA"
    API = "API"
    EVENT = "EVENT"
    QUEUE = "QUEUE"
    AGENT = "AGENT"
    DATABASE = "DATABASE"
    MODEL = "MODEL"
    TOOL = "TOOL"

@dataclass
class CapabilityRelationship:
    """A directed semantic connection between two capabilities in the system graph."""
    id: uuid.UUID
    repository_id: uuid.UUID
    source_capability_id: uuid.UUID
    target_capability_id: uuid.UUID
    relationship_type: str  # DEPENDS_ON, USES, SUPPORTS, IMPLEMENTS, EXPOSES, CONSUMES, PROVIDES, ORCHESTRATES, OWNED_BY, PART_OF
    dependency_type: CapabilityDependencyType = CapabilityDependencyType.API
