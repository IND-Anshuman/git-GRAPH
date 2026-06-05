"""Domain entity representing a directional transition between two logic versions."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.domain.enums.transition_type import TransitionType
from src.domain.exceptions import InvalidEntityException


@dataclass
class LogicTransition:
    """
    A LogicTransition records how a logic implementation changed between two commits.

    It connects a source LogicVersion (from) to a target LogicVersion (to) and
    classifies the nature of the change.  Either from or to may be None for
    CREATED/DELETED transitions, but not both simultaneously.
    """

    id: uuid.UUID
    """Unique identifier for this transition record."""

    from_logic_version_id: uuid.UUID | None
    """Source version ID. None when transition_type is CREATED."""

    to_logic_version_id: uuid.UUID | None
    """Target version ID. None when transition_type is DELETED."""

    transition_type: TransitionType
    """Classification of the change that occurred."""

    similarity_score: float
    """Cosine or structural similarity in [0.0, 1.0] between the two logic fingerprints."""

    overall_confidence: float = 1.0
    """Confidence in the correctness of this transition classification."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Arbitrary extensible metadata (e.g., matched rule IDs, reviewer notes)."""

    created_at: datetime = field(default_factory=datetime.utcnow)
    """UTC timestamp when this transition was computed."""

    def validate(self) -> None:
        """
        Validate the invariants of this LogicTransition.

        Raises:
            InvalidEntityException: If similarity_score is out of [0.0, 1.0] or
                both version IDs are None at the same time.
        """
        if not (0.0 <= self.similarity_score <= 1.0):
            raise InvalidEntityException(
                f"LogicTransition.similarity_score must be in [0.0, 1.0], "
                f"got {self.similarity_score} (id={self.id})"
            )
        if self.from_logic_version_id is None and self.to_logic_version_id is None:
            raise InvalidEntityException(
                f"LogicTransition cannot have both from_logic_version_id and "
                f"to_logic_version_id set to None (id={self.id})"
            )
