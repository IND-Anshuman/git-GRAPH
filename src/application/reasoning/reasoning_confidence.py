"""
Phase 7A — ReasoningConfidence

Encapsulates the confidence *score* (float in [0.0, 1.0]) produced by the
HypothesisScoringEngine and translates it into a human-readable *level*.

Confidence formula
------------------
The weighted coverage score is calculated as::

    score = Σ(weight_i * presence_i) / Σ(weight_i)

where *presence_i* is 1.0 if source_i was found in the validated evidence
set and 0.0 otherwise, and *weight_i* comes from EvidenceWeightRegistry.

Level thresholds
----------------
  HIGH    ≥ 0.80
  MEDIUM  ≥ 0.55
  LOW     ≥ 0.30
  MINIMAL  < 0.30
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Human-readable tier for the numeric confidence score."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


@dataclass(frozen=True)
class ReasoningConfidence:
    """Immutable holder for a reasoning run's confidence score and level."""

    score: float
    """Weighted coverage score in [0.0, 1.0]."""

    level: ConfidenceLevel
    """Human-readable tier derived from the score."""

    rationale: str
    """One-sentence explanation of why this confidence was assigned."""

    # ── Factory ───────────────────────────────────────────────────────────────

    @classmethod
    def from_score(cls, score: float, rationale: str = "") -> "ReasoningConfidence":
        """Build a :class:`ReasoningConfidence` from a raw numeric score."""
        if not (0.0 <= score <= 1.0):
            raise ValueError(f"Confidence score must be in [0.0, 1.0], got {score!r}")

        if score >= 0.80:
            level = ConfidenceLevel.HIGH
        elif score >= 0.55:
            level = ConfidenceLevel.MEDIUM
        elif score >= 0.30:
            level = ConfidenceLevel.LOW
        else:
            level = ConfidenceLevel.MINIMAL

        return cls(score=round(score, 4), level=level, rationale=rationale)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @classmethod
    def compute(
        cls,
        weights: dict[str, float],
        found_types: set[str],
        rationale: str = "",
    ) -> "ReasoningConfidence":
        """Compute confidence from a weight dict and the set of evidence types found.

        Args:
            weights:     Mapping of evidence_type → weight (from EvidenceWeightRegistry).
            found_types: Set of evidence type keys actually present in the validated set.
            rationale:   Human-readable explanation string.

        Returns:
            A :class:`ReasoningConfidence` instance.
        """
        total_weight = sum(weights.values())
        if total_weight == 0.0:
            return cls.from_score(0.0, rationale or "No weighted evidence available.")

        achieved = sum(w for k, w in weights.items() if k in found_types)
        score = achieved / total_weight
        return cls.from_score(min(score, 1.0), rationale)

    def __str__(self) -> str:
        return f"{self.level.value} ({self.score:.2%})"
