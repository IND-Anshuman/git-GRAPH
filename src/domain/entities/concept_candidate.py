"""Domain entity representing a proposed concept candidate."""

import uuid
from dataclasses import dataclass, field
from src.domain.value_objects.candidate_evidence import CandidateEvidence


@dataclass
class ConceptCandidate:
    """A discovered candidate representing a high-level concept before official promotion."""

    id: uuid.UUID
    name: str
    confidence: float
    evidence: CandidateEvidence
    ontology_parent_candidate: str | None = None
    status: str = "CANDIDATE"  # CANDIDATE, APPROVED, REJECTED, DEPRECATED

    def validate(self) -> None:
        """Validates invariants of the ConceptCandidate."""
        if not self.name or not self.name.strip():
            raise ValueError("ConceptCandidate.name must not be empty.")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("ConceptCandidate.confidence must be in [0.0, 1.0].")
        if self.status not in ("CANDIDATE", "APPROVED", "REJECTED", "DEPRECATED"):
            raise ValueError(f"ConceptCandidate.status is invalid: {self.status}")
