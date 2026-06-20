from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from .intent_type import IntentType
from .intent_confidence import IntentConfidence
from .intent_evidence import IntentEvidence

@dataclass
class Intent:
    id: UUID
    name: str
    intent_type: IntentType
    description: str
    confidence: IntentConfidence
    evidence: IntentEvidence
    repository_id: str
    first_seen_at: datetime
    last_seen_at: datetime
    supporting_decisions: list[str] = field(default_factory=list)
