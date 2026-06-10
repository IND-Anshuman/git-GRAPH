"""Intermediate Semantic Representation: CanonicalRelationship definition."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from src.domain.value_objects.semantic_relationship_type import SemanticRelationshipType


@dataclass
class CanonicalRelationship:
    """Represents a language-neutral semantic link between entities."""

    id: str
    from_entity_id: str
    to_entity_id: str
    relationship_type: str  # CALLS, INJECTS, SENDS, USES_TOOL, AWAITS, SENDS, RECEIVES, etc.
    confidence: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    semantic_relationship_type: Optional[SemanticRelationshipType] = None

