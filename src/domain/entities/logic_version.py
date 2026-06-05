"""Domain entity representing one concrete implementation of a logic signature at a commit."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.domain.exceptions import InvalidEntityException
from src.domain.value_objects.confidence_breakdown import ConfidenceBreakdown
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.logic_fingerprint import LogicFingerprint


@dataclass
class LogicVersion:
    """
    A LogicVersion captures one specific, fingerprinted implementation of a
    LogicSignature as it existed at a particular commit.

    Each time a commit modifies the code entity that contains the logic,
    a new LogicVersion is created and linked to the previous one via a
    LogicTransition, forming a traceable evolution chain.
    """

    id: uuid.UUID
    """Unique identifier for this logic version record."""

    logic_signature_id: uuid.UUID
    """Reference to the parent LogicSignature this version belongs to."""

    code_entity_seid: SEID
    """The SEID of the CodeEntity that contains this implementation."""

    commit_hash: str
    """The VCS commit at which this version was observed."""

    version_ordinal: int
    """Monotonically increasing sequence number within the signature's history (>= 1)."""

    fingerprint: LogicFingerprint
    """Multi-dimensional fingerprint uniquely identifying this exact implementation."""

    overall_confidence: float = 1.0
    """Aggregate detection confidence in [0.0, 1.0]."""

    confidence_breakdown: ConfidenceBreakdown | None = None
    """Optional detailed confidence breakdown by signal type."""

    is_primary: bool = False
    """True if this is the canonical version for the commit (vs. an alternative candidate)."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Arbitrary extensible metadata."""

    created_at: datetime = field(default_factory=datetime.utcnow)
    """UTC timestamp when this record was created."""

    def validate(self) -> None:
        """
        Validate the invariants of this LogicVersion.

        Raises:
            InvalidEntityException: If version_ordinal < 1 or confidence is out of [0.0, 1.0].
        """
        if self.version_ordinal < 1:
            raise InvalidEntityException(
                f"LogicVersion.version_ordinal must be >= 1, got {self.version_ordinal} "
                f"(id={self.id})"
            )
        if not (0.0 <= self.overall_confidence <= 1.0):
            raise InvalidEntityException(
                f"LogicVersion.overall_confidence must be in [0.0, 1.0], "
                f"got {self.overall_confidence} (id={self.id})"
            )
