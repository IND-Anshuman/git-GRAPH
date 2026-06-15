"""Domain model representing evidence supporting a capability discovery."""

from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class CapabilityEvidence:
    """Aggregated evidence that justifies the discovery of a capability."""
    concepts: List[str] = field(default_factory=list)
    behaviors: List[str] = field(default_factory=list)
    flows: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    supporting_relationships: List[str] = field(default_factory=list)
    confidence_breakdown: Dict[str, Any] = field(default_factory=dict)
