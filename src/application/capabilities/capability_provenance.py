"""Domain model representing capability provenance and explainability."""

from dataclasses import dataclass, field
from typing import List

@dataclass
class CapabilityProvenance:
    """Explainability record tracking the origin and configuration of a capability."""
    capability_id: str
    source_concepts: List[str] = field(default_factory=list)
    source_behaviors: List[str] = field(default_factory=list)
    source_flows: List[str] = field(default_factory=list)
    source_entities: List[str] = field(default_factory=list)
    discovery_algorithm: str = "hierarchical_clustering"
    discovery_version: str = "1.0.0"
    placement_score: float = 0.0
    creation_commit: str = ""
