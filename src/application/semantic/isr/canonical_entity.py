"""Intermediate Semantic Representation: CanonicalEntity definition."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from src.domain.value_objects.code_location import CodeLocation


@dataclass
class CanonicalEntity:
    """Represents a language-neutral semantic code or architectural block."""

    id: str
    name: str
    qualified_name: str
    entity_type: str  # Class, Method, Controller, Service, DTO, Agent, Coroutine, Topic, etc.
    visibility: str = "public"
    return_type: Optional[str] = None
    generics: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    location: Optional[CodeLocation] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
