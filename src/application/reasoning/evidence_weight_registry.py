"""
Phase 7A — EvidenceWeightRegistry

Stores the canonical, static confidence weights that the
HypothesisScoringEngine applies when evaluating evidence nodes.

Design rationale
----------------
Weights express how *trustworthy* each source type is:

  CAPABILITY  1.00  — compiled and validated; highest trust
  FLOW        0.95  — inferred from multiple signals; very high trust
  ENTITY      0.90  — directly extracted from source code
  RELATIONSHIP 0.85  — inferred structural relationship
  CONCEPT     0.80  — semantic concept (may be approximate)
  ARTIFACT    0.75  — compiler output; still validated but derivative
  DEPENDENCY  0.70  — inferred dependency; can be incomplete
  TIMELINE    0.65  — temporal data; subject to incomplete history

All weights are in range [0.0, 1.0].  The registry is intentionally
a plain class with class-level constants so that type-checkers and
linters can resolve them statically without any runtime registration.
"""

from __future__ import annotations


class EvidenceWeightRegistry:
    """Static registry of evidence confidence weights.

    Usage::

        weight = EvidenceWeightRegistry.get("capability")
        # 1.0
    """

    # ── Weight constants ──────────────────────────────────────────────────────
    CAPABILITY: float = 1.00
    FLOW: float = 0.95
    ENTITY: float = 0.90
    RELATIONSHIP: float = 0.85
    CONCEPT: float = 0.80
    ARTIFACT: float = 0.75
    DEPENDENCY: float = 0.70
    TIMELINE: float = 0.65
    OWNERSHIP: float = 0.60
    UNKNOWN: float = 0.40

    # ── Canonical lookup map ──────────────────────────────────────────────────
    _REGISTRY: dict[str, float] = {
        "capability": CAPABILITY,
        "flow": FLOW,
        "entity": ENTITY,
        "relationship": RELATIONSHIP,
        "concept": CONCEPT,
        "artifact": ARTIFACT,
        "dependency": DEPENDENCY,
        "timeline": TIMELINE,
        "ownership": OWNERSHIP,
    }

    @classmethod
    def get(cls, evidence_type: str) -> float:
        """Return the weight for *evidence_type*, falling back to UNKNOWN."""
        return cls._REGISTRY.get(evidence_type.lower(), cls.UNKNOWN)

    @classmethod
    def all_weights(cls) -> dict[str, float]:
        """Return a copy of all registered weights."""
        return dict(cls._REGISTRY)
