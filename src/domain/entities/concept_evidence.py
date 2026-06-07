"""Domain entity representing a granular audit link from a concept version to behavioral/logic evidence."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from src.domain.exceptions import InvalidEntityException


@dataclass
class ConceptEvidence:
    """
    ConceptEvidence links a ConceptVersion to supporting LogicVersion
    or LogicEvidence entries, providing a deterministic audit path.
    """

    id: uuid.UUID
    """Unique identifier of this evidence link."""

    concept_version_id: uuid.UUID
    """The parent ConceptVersion ID."""

    evidence_type: str
    """Type of supporting evidence (e.g. 'LOGIC_VERSION', 'LOGIC_EVIDENCE')."""

    target_id: uuid.UUID
    """The UUID of the supporting LogicVersion or LogicEvidence entity."""

    confidence_contribution: float
    """The weight/contribution score of this evidence, in [0.00, 1.00]."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Audit triggers and AST feature snapshots."""

    created_at: datetime = field(default_factory=datetime.utcnow)
    """Timestamp when this evidence link was recorded."""

    def validate(self) -> None:
        """
        Validate ConceptEvidence invariants.

        Raises:
            InvalidEntityException: If out of bounds.
        """
        if not (0.00 <= self.confidence_contribution <= 1.00):
            raise InvalidEntityException("confidence_contribution must be between 0.00 and 1.00.")
        if not self.evidence_type:
            raise InvalidEntityException("evidence_type must not be empty.")
