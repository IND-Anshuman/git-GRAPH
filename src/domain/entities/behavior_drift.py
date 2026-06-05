"""Domain entity representing measured behavioral drift between two logic versions."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.domain.enums.drift_category import DriftCategory
from src.domain.value_objects.drift_dimensions import DriftDimensions


@dataclass
class BehaviorDrift:
    """
    A BehaviorDrift record quantifies how much the behavior of a logic implementation
    changed between two consecutive LogicVersions connected by a LogicTransition.

    Dimension scores are stored alongside an overall drift score and a categorical
    label so that consumers can quickly filter by severity without recomputing.
    """

    id: uuid.UUID
    """Unique identifier for this drift record."""

    logic_transition_id: uuid.UUID
    """Reference to the LogicTransition that triggered this drift measurement."""

    from_logic_version_id: uuid.UUID
    """Source LogicVersion ID (before the change)."""

    to_logic_version_id: uuid.UUID
    """Target LogicVersion ID (after the change)."""

    drift_score: float
    """Aggregate drift score in [0.0, 1.0] computed from dimension_scores."""

    drift_category: DriftCategory
    """Categorical severity label derived from drift_score."""

    dimension_scores: DriftDimensions
    """Fine-grained drift breakdown across structural, dependency, and other axes."""

    ontology_changed: bool = False
    """True if the ontology classification changed between the two versions."""

    security_boundary_crossed: bool = False
    """True if a security-relevant threshold was crossed (e.g., weaker algorithm substituted)."""

    computed_at: datetime = field(default_factory=datetime.utcnow)
    """UTC timestamp when this drift was computed."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Arbitrary extensible metadata."""

    @classmethod
    def classify_category(cls, drift_score: float) -> DriftCategory:
        """
        Map a numeric drift score to a DriftCategory enum value.

        Thresholds:
            [0.00, 0.10) → TRIVIAL
            [0.10, 0.30) → MINOR
            [0.30, 0.60) → SIGNIFICANT
            [0.60, 0.85) → MAJOR
            [0.85, 1.00] → COMPLETE

        Args:
            drift_score: A float in [0.0, 1.0].

        Returns:
            The matching DriftCategory.
        """
        if drift_score < 0.10:
            return DriftCategory.TRIVIAL
        if drift_score < 0.30:
            return DriftCategory.MINOR
        if drift_score < 0.60:
            return DriftCategory.SIGNIFICANT
        if drift_score < 0.85:
            return DriftCategory.MAJOR
        return DriftCategory.COMPLETE
