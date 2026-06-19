"""Domain model representing ownership and knowledge distribution in the architecture."""

import uuid
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class OwnershipProfile:
    """Ownership, silos, and bus factors for the architecture."""
    id: uuid.UUID
    repository_id: str
    commit_hash: str
    capability_ownership: dict[str, list[str]] = field(default_factory=dict)
    knowledge_silos: list[str] = field(default_factory=list)
    bus_factor_risks: list[dict] = field(default_factory=list)
    unowned_capabilities: list[str] = field(default_factory=list)
    overloaded_teams: list[dict] = field(default_factory=list)
    ownership_drift: list[dict] = field(default_factory=list)
    evidence_sources: list[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.utcnow)
