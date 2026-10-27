"""Domain model representing evidence supporting a capability discovery."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CapabilityEvidence:
    """Aggregated evidence that justifies the discovery of a capability."""

    concepts: list[str] = field(default_factory=list)
    behaviors: list[str] = field(default_factory=list)
    flows: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    supporting_relationships: list[str] = field(default_factory=list)
    confidence_breakdown: dict[str, Any] = field(default_factory=dict)
