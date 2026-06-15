"""Domain model representing a capability candidate."""

import uuid
from dataclasses import dataclass, field
from src.application.capabilities.capability_evidence import CapabilityEvidence

@dataclass
class CapabilityCandidate:
    """A capability proposed by the discovery engine before formal governance approval."""
    id: uuid.UUID
    name: str
    description: str
    confidence: float
    status: str = "CANDIDATE"  # CANDIDATE, APPROVED, REJECTED, MERGED, DEPRECATED
    evidence: CapabilityEvidence = field(default_factory=CapabilityEvidence)
    capability_type: str = "TECHNICAL"

    def validate(self) -> None:
        """Validates invariants of the CapabilityCandidate."""
        if not self.name or not self.name.strip():
            raise ValueError("CapabilityCandidate.name must not be empty.")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("CapabilityCandidate.confidence must be in [0.0, 1.0].")
        if self.status not in ("CANDIDATE", "APPROVED", "REJECTED", "MERGED", "DEPRECATED"):
            raise ValueError(f"CapabilityCandidate.status is invalid: {self.status}")
