from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from .causal_relationship import CausalRelationship

@dataclass
class CausalChain:
    chain_id: UUID
    repository_id: str
    root_cause_id: UUID
    summary: str
    confidence: float
    generated_at: datetime
    relationships: list[CausalRelationship] = field(default_factory=list)
