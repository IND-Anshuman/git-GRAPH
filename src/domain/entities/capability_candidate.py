"""Domain entity representing a proposed business or technical capability candidate."""

import uuid
from dataclasses import dataclass
from src.domain.value_objects.candidate_evidence import CandidateEvidence


@dataclass
class CapabilityCandidate:
    """A discovered candidate representing a macro business/technical capability before official validation."""

    id: uuid.UUID
    name: str
    confidence: float
    evidence: CandidateEvidence
    status: str = "CANDIDATE"  # CANDIDATE, APPROVED, REJECTED, DEPRECATED

    def validate(self) -> None:
        """Validates invariants of the CapabilityCandidate."""
        if not self.name or not self.name.strip():
            raise ValueError("CapabilityCandidate.name must not be empty.")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("CapabilityCandidate.confidence must be in [0.0, 1.0].")
        if self.status not in ("CANDIDATE", "APPROVED", "REJECTED", "DEPRECATED"):
            raise ValueError(f"CapabilityCandidate.status is invalid: {self.status}")
