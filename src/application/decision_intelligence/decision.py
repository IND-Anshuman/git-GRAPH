from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from .decision_type import DecisionType
from .decision_status import DecisionStatus
from .decision_confidence import DecisionConfidence
from .decision_version import DecisionVersion
from .decision_evidence import DecisionEvidence

@dataclass
class Decision:
    id: UUID
    name: str
    description: str
    decision_type: DecisionType
    confidence: DecisionConfidence
    status: DecisionStatus
    created_at: datetime
    first_seen_commit: str
    last_seen_commit: str
    repository_id: str
    versions: list[DecisionVersion] = field(default_factory=list)
    supporting_evidence: DecisionEvidence = field(default_factory=DecisionEvidence)
    affected_capabilities: list[str] = field(default_factory=list)
    affected_architectures: list[str] = field(default_factory=list)
    affected_services: list[str] = field(default_factory=list)
