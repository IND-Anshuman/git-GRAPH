"""Intermediate Semantic Representation: CanonicalFlow definition."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CanonicalFlow:
    """Represents a first-class execution path tracing interactions across entities."""

    id: str
    flow_type: str  # REQUEST_RESPONSE_FLOW, AI_AGENT_WORKFLOW, EVENT_FLOW, etc.
    source_entity_id: str
    target_entity_id: str
    intermediate_entities: List[str] = field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
