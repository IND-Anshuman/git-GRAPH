"""
Phase 7A — ReasoningEvidence

A single piece of evidence used to support or refute a reasoning hypothesis.
Evidence carries an explicit *source_type* (matched against EvidenceWeightRegistry),
a *weight*, and a *validated* flag that the EvidenceValidationLayer sets after
confirming the referenced entity's physical existence in the database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReasoningEvidence:
    """One validated piece of evidence collected from the knowledge graph.

    Attributes:
        source_id:    Unique identifier of the evidence source (e.g. entity_id,
                      capability_id, flow_id).
        source_type:  Category string matching keys in EvidenceWeightRegistry
                      (``"capability"``, ``"flow"``, ``"entity"``, …).
        description:  Human-readable summary of what this evidence says.
        weight:       Numeric confidence weight in [0.0, 1.0].  Typically
                      pre-populated from EvidenceWeightRegistry by the
                      collection engine.
        validated:    Set to True by EvidenceValidationLayer once the source_id
                      is confirmed present in the database.
        metadata:     Arbitrary extra data for debugging / display (file path,
                      commit hash, line number, etc.).
    """

    source_id: str
    source_type: str
    description: str
    weight: float = 1.0
    validated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def validate_weight(self) -> None:
        """Raise ValueError if weight is outside [0.0, 1.0]."""
        if not (0.0 <= self.weight <= 1.0):
            raise ValueError(
                f"ReasoningEvidence.weight must be in [0.0, 1.0], got {self.weight!r} "
                f"for source_id={self.source_id!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "description": self.description,
            "weight": self.weight,
            "validated": self.validated,
            "metadata": self.metadata,
        }
