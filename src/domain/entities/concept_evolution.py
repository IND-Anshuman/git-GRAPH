"""Domain entity representing a chronological evolution link between concept versions."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from src.domain.enums.concept_transition_type import ConceptTransitionType
from src.domain.exceptions import InvalidEntityException


@dataclass
class ConceptEvolution:
    """
    ConceptEvolution stores evolutionary transition edges (e.g. SPLIT, MERGE, CREATION)
    linking sequential versions of a concept across commits.
    """

    id: uuid.UUID
    """Unique identifier for this evolution link."""

    from_concept_version_id: uuid.UUID | None
    """The predecessor version ID (None if first creation)."""

    to_concept_version_id: uuid.UUID
    """The successor version ID."""

    transition_type: ConceptTransitionType
    """The type of evolutionary event (e.g. CONCEPT_SPLIT)."""

    similarity_score: float
    """Overlap similarity score in [0.00, 1.00]."""

    created_at: datetime = field(default_factory=datetime.utcnow)
    """Timestamp when this transition link was created."""

    def validate(self) -> None:
        """
        Validate ConceptEvolution invariants.

        Raises:
            InvalidEntityException: If out of bounds.
        """
        if self.from_concept_version_id is None and self.transition_type != ConceptTransitionType.CONCEPT_CREATION:
            raise InvalidEntityException(
                "predecessor ID can only be None for CONCEPT_CREATION transitions."
            )
        if not (0.00 <= self.similarity_score <= 1.00):
            raise InvalidEntityException("similarity_score must be in [0.00, 1.00].")
