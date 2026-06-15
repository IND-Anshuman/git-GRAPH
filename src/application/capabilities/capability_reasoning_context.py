"""Domain model representing capability reasoning contexts."""

import uuid
from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class CapabilityReasoningContext:
    """Canonical reasoning object that aggregates all metadata, scores, and links for a capability."""
    capability_id: uuid.UUID
    summary: str
    ownership: List[Dict[str, Any]]
    health: Dict[str, Any]
    risk: Dict[str, Any]
    drift: Dict[str, Any]
    dependencies: List[Dict[str, Any]]
    blast_radius: Dict[str, Any]
    stability: str
    confidence: float
    provenance: Dict[str, Any]
    cohesion: Dict[str, Any]
    coupling: Dict[str, Any]
    boundary: Dict[str, Any]
