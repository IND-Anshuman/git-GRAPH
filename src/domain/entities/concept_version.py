"""Domain entity representing a point-in-time version of a concept at a specific commit."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from src.domain.exceptions import InvalidEntityException


@dataclass
class ConceptVersion:
    """
    A ConceptVersion represents the state and confidence of a ConceptNode
    at a specific Git commit.
    """

    id: uuid.UUID
    """Unique identifier for this concept version."""

    concept_id: uuid.UUID
    """The associated ConceptNode ID."""

    commit_hash: str
    """VCS commit hash this version snapshot corresponds to."""

    version_number: int
    """Monotonically increasing version number starting at 1."""

    confidence: float
    """Confidence score clamped strictly in [0.05, 1.00]."""

    is_active: bool = True
    """True if active, False if deleted/inactive at this commit."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Extensible metadata payload."""

    created_at: datetime = field(default_factory=datetime.utcnow)
    """Timestamp when this version snapshot was recorded."""

    def validate(self) -> None:
        """
        Validate ConceptVersion invariants.

        Raises:
            InvalidEntityException: If values are out of bounds.
        """
        if self.version_number < 1:
            raise InvalidEntityException("version_number must be greater than or equal to 1.")
        if not (0.05 <= self.confidence <= 1.00):
            raise InvalidEntityException("confidence must be clamped between 0.05 and 1.00.")
        if not self.commit_hash or len(self.commit_hash) != 40:
            raise InvalidEntityException("commit_hash must be a valid 40-character sha.")
