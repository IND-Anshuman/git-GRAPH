"""
Phase 7A — HypothesisScoringEngine

Scores each ``ReasoningHypothesis`` in ``context.hypotheses`` using the
weighted evidence coverage formula from ``EvidenceWeightRegistry`` and
selects the best-scoring hypothesis as ``context.selected_hypothesis``.

Scoring formula
---------------
For each hypothesis H:

    score(H) = Σ(weight_i) for each supporting evidence_i
               ─────────────────────────────────────────────
               Σ(weight_i) for ALL validated evidence

Meaning: a hypothesis that is supported by HIGH-weight evidence types
(capability > flow > entity > …) gets a higher score.

Tie-breaking: the hypothesis with the longest ``supporting_ids`` list wins.
"""

from __future__ import annotations

import logging

from src.application.reasoning.reasoning_context import ReasoningContext
from src.application.reasoning.evidence_weight_registry import EvidenceWeightRegistry
from src.application.reasoning.reasoning_confidence import ReasoningConfidence

logger = logging.getLogger(__name__)


class HypothesisScoringEngine:
    """Scores and ranks hypotheses; selects the best explanation."""

    def score(self, context: ReasoningContext) -> None:
        """Score all hypotheses in *context* and select the best one.

        Side effects:
            * Sets ``hypothesis.score`` for every hypothesis.
            * Sets ``hypothesis.is_selected = True`` for the winner.
            * Sets ``context.selected_hypothesis``.
            * Sets ``context.confidence``.

        Args:
            context: Mutable pipeline carry-bag (modified in-place).
        """
        if not context.hypotheses:
            context.chain.add_step(
                step_type="hypothesis_scoring",
                description="No hypotheses to score; setting zero confidence.",
            )
            context.confidence = ReasoningConfidence.from_score(
                0.0, "No hypotheses generated — insufficient evidence."
            )
            return

        # Build a weight index for validated evidence
        evidence_weights: dict[str, float] = {
            ev.source_id: ev.weight
            for ev in context.validated_evidence
        }
        total_weight = sum(evidence_weights.values())

        context.chain.add_step(
            step_type="hypothesis_scoring",
            description=(
                f"Scoring {len(context.hypotheses)} hypothesis/hypotheses against "
                f"{len(evidence_weights)} evidence nodes "
                f"(total_weight={total_weight:.3f})."
            ),
        )

        for hypothesis in context.hypotheses:
            if total_weight == 0.0:
                hypothesis.score = 0.0
                continue
            supported_weight = sum(
                evidence_weights.get(sid, 0.0)
                for sid in hypothesis.supporting_ids
            )
            hypothesis.score = min(1.0, supported_weight / total_weight)
            hypothesis.rationale = (
                f"Supported by {len(hypothesis.supporting_ids)} evidence node(s) "
                f"with total weight {supported_weight:.3f} / {total_weight:.3f}."
            )

        # Sort descending by score, then by supporting count as tiebreaker
        ranked = sorted(
            context.hypotheses,
            key=lambda h: (h.score, len(h.supporting_ids)),
            reverse=True,
        )

        # Select winner
        winner = ranked[0]
        winner.is_selected = True
        context.selected_hypothesis = winner
        context.hypotheses = [h for h in ranked if not h.is_selected]

        # Compute overall confidence from evidence type coverage
        found_types = context.all_collected_source_types()
        context.confidence = ReasoningConfidence.compute(
            weights=EvidenceWeightRegistry.all_weights(),
            found_types=found_types,
            rationale=(
                f"Best hypothesis scored {winner.score:.2%} "
                f"from {len(winner.supporting_ids)} evidence node(s). "
                f"Evidence types: {', '.join(sorted(found_types)) or 'none'}."
            ),
        )

        context.chain.add_step(
            step_type="hypothesis_scoring_complete",
            description=(
                f"Selected hypothesis id={winner.hypothesis_id!r} "
                f"score={winner.score:.4f}, confidence={context.confidence}."
            ),
            outputs=[winner.hypothesis_id],
        )
