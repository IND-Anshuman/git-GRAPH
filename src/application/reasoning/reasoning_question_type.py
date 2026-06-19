"""
Phase 7A — ReasoningQuestionType

Classifies what kind of reasoning question the user has asked.
The QueryPlanner and ReasoningStrategyRegistry use this classification
to route execution to the correct IReasoningStrategy implementation.

Adding a new question type here (and a corresponding strategy) is the
*only* change required when 7B/7C introduce new reasoning modes.
"""

from enum import Enum


class ReasoningQuestionType(str, Enum):
    """Taxonomy of questions the Reasoning Intelligence Layer can answer."""

    # ── Causal / Explanatory ──────────────────────────────────────────────────
    WHY = "why"
    """Why does X exist / behave this way?"""

    ROOT_CAUSE = "root_cause"
    """What is the root cause of incident / anomaly Y?"""

    CAUSAL = "causal"
    """How does A causally affect B?"""

    # ── Impact / Risk ─────────────────────────────────────────────────────────
    BLAST_RADIUS = "blast_radius"
    """What breaks if X changes / fails?"""

    RISK = "risk"
    """What are the current risk exposures?"""

    # ── Structural / Architectural ────────────────────────────────────────────
    ARCHITECTURE = "architecture"
    """What are the architectural patterns / boundaries?"""

    DEPENDENCY = "dependency"
    """What does X depend on?  / What depends on X?"""

    # ── Temporal / Evolutionary ───────────────────────────────────────────────
    DRIFT = "drift"
    """How has X drifted from its original design?"""

    EVOLUTION = "evolution"
    """How has X evolved over time?"""

    # ── Ownership / Governance ────────────────────────────────────────────────
    OWNERSHIP = "ownership"
    """Who owns X?"""

    # ── Counterfactual ────────────────────────────────────────────────────────
    COUNTERFACTUAL = "counterfactual"
    """What would happen if we changed X?"""

    # ── Decision / Intent (Phase 7C placeholders) ─────────────────────────────
    DECISION = "decision"
    """Why was architectural decision D made?"""

    INTENT = "intent"
    """What is the intended business purpose of X?"""

    # ── Phase 7B Architectural Intelligence ───────────────────────────────────
    ARCHITECTURE_STYLE = "architecture_style"
    FITNESS = "fitness"
    INVARIANT = "invariant"
    DRIFT_ARCH = "drift_arch"
    OWNERSHIP_ARCH = "ownership_arch"
    REFACTORING = "refactoring"
    RECOMMENDATION = "recommendation"
    SIMILARITY = "similarity"
    BENCHMARK = "benchmark"
    TIMELINE = "timeline"

    # ── Catch-all ─────────────────────────────────────────────────────────────
    GENERAL = "general"
    """Unclassified question — handled by the default strategy."""
