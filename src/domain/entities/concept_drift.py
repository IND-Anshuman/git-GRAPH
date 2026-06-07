"""Domain entity representing conceptual drift metrics."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from src.domain.exceptions import InvalidEntityException


@dataclass
class ConceptDrift:
    """
    ConceptDrift records computed behavioral, structural, and dependency drift
    for a concept across commits.
    """

    id: uuid.UUID
    """Unique identifier for this drift record."""

    concept_id: uuid.UUID
    """The associated ConceptNode ID."""

    baseline_commit: str
    """Git commit serving as the comparison baseline."""

    current_commit: str
    """Git commit representing the current state."""

    drift_score: float
    """Unified drift index score in [0.00, 1.00]."""

    drift_category: str
    """Label for drift severity (TRIVIAL, MINOR, SIGNIFICANT, MAJOR, COMPLETE)."""

    dimension_scores: Dict[str, float]
    """Sub-scores mapping drift by dimension (structural, pattern, dependency)."""

    computed_at: datetime = field(default_factory=datetime.utcnow)
    """Timestamp when this drift score was calculated."""

    def validate(self) -> None:
        """
        Validate ConceptDrift invariants.

        Raises:
            InvalidEntityException: If out of bounds.
        """
        if not (0.00 <= self.drift_score <= 1.00):
            raise InvalidEntityException("drift_score must be in [0.00, 1.00].")
        if not self.baseline_commit or not self.current_commit:
            raise InvalidEntityException("commits must not be empty.")
        if not self.drift_category:
            raise InvalidEntityException("drift_category must not be empty.")
