"""
Phase 7C — DecisionFitnessEngine

Computes multi-dimensional fitness scores for a Decision based on real
evidence derived from:

    - DecisionVersion history (stability / churn)
    - Temporal longevity (first_seen_commit date vs. now)
    - Evidence coverage (number of supporting commits / documents)
    - ADR confirmation status (artifact agreement)
    - Architecture / capability impact breadth (adoption footprint)

Fitness Dimensions:
─────────────────
    longevity_score     How long the decision has been active relative to a
                        reference maximum lifespan of MAX_LIFESPAN_DAYS.

    stability_score     Inverse of version churn rate:
                        1 - min(1.0, (version_count - 1) / CHURN_THRESHOLD)
                        A decision that has never changed has stability = 1.0.

    impact_score        Breadth of impact: normalised count of affected
                        capabilities + architectures + services.

    adoption_score      Evidence density: normalised count of unique supporting
                        commits and documents. Saturates at ADOPTION_SAT_THRESHOLD.

    success_rate        Composite proxy for decision health:
                        - Weighted 0.50 on confidence.score
                        - Weighted 0.30 on status (ACTIVE=1.0, PROPOSED=0.6,
                          DEPRECATED=0.3, SUPERSEDED/REVERTED=0.1)
                        - Weighted 0.20 on ADR confirmation (any supporting document)

    overall_fitness     Weighted blend:
                        0.25×longevity + 0.20×stability + 0.20×impact
                        + 0.20×adoption + 0.15×success_rate
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from .decision import Decision
from .decision_fitness import DecisionFitness
from .decision_status import DecisionStatus

logger = logging.getLogger(__name__)

# ─── Tuneable constants ────────────────────────────────────────────────────────
MAX_LIFESPAN_DAYS: int = 730          # 2 years = longevity_score of 1.0
CHURN_THRESHOLD: int = 5              # 5 versions without stabilising → stability = 0.0
IMPACT_SAT_ITEMS: int = 10           # ≥10 affected items → impact_score = 1.0
ADOPTION_SAT_COMMITS: int = 8        # ≥8 supporting commits → adoption_score = 1.0
ADOPTION_SAT_DOCS: int = 3           # ≥3 supporting docs → adoption bonus

_STATUS_HEALTH: dict[DecisionStatus, float] = {
    DecisionStatus.ACTIVE:      1.00,
    DecisionStatus.PROPOSED:    0.60,
    DecisionStatus.DEPRECATED:  0.30,
    DecisionStatus.SUPERSEDED:  0.10,
    DecisionStatus.REVERTED:    0.05,
}

_WEIGHTS = {
    "longevity":   0.25,
    "stability":   0.20,
    "impact":      0.20,
    "adoption":    0.20,
    "success":     0.15,
}


class DecisionFitnessEngine:
    """
    Evaluates the fitness of a Decision based on its full version history and
    evidence record.

    All scores are in [0.0, 1.0].  Higher = healthier / more fit.

    Usage::

        engine = DecisionFitnessEngine()
        fitness = engine.evaluate_fitness(decision)
    """

    def evaluate_fitness(
        self,
        decision: Decision,
        reference_date: Optional[datetime] = None,
    ) -> DecisionFitness:
        """
        Compute and return an immutable :class:`DecisionFitness` value object.

        Args:
            decision:       The :class:`Decision` domain object to evaluate.
            reference_date: The "now" date used for longevity computation.
                            Defaults to ``datetime.now(timezone.utc)``.
        """
        now = reference_date or datetime.now(timezone.utc)

        longevity  = self._compute_longevity(decision, now)
        stability  = self._compute_stability(decision)
        impact     = self._compute_impact(decision)
        adoption   = self._compute_adoption(decision)
        success    = self._compute_success_rate(decision)

        overall = round(
            _WEIGHTS["longevity"] * longevity
            + _WEIGHTS["stability"] * stability
            + _WEIGHTS["impact"]    * impact
            + _WEIGHTS["adoption"]  * adoption
            + _WEIGHTS["success"]   * success,
            4,
        )

        logger.debug(
            "DecisionFitnessEngine: '%s' → longevity=%.2f stability=%.2f "
            "impact=%.2f adoption=%.2f success=%.2f overall=%.3f",
            decision.name,
            longevity, stability, impact, adoption, success, overall,
        )

        return DecisionFitness(
            decision_id=decision.id,
            longevity_score=round(longevity, 4),
            stability_score=round(stability, 4),
            impact_score=round(impact, 4),
            adoption_score=round(adoption, 4),
            success_rate=round(success, 4),
            overall_fitness=overall,
            evaluated_at=now,
        )

    # ─────────────────────────────────────────────────────────────────────────
    #  Dimension calculators
    # ─────────────────────────────────────────────────────────────────────────

    def _compute_longevity(self, decision: Decision, now: datetime) -> float:
        """
        Measures how long the decision has been alive.

        Uses decision.created_at for the birth date.  If unavailable, returns 0.
        """
        birth = decision.created_at
        if birth is None:
            return 0.0

        # Make timezone-aware for comparison
        if birth.tzinfo is None:
            birth = birth.replace(tzinfo=timezone.utc)

        age_days = (now - birth).days
        return min(1.0, age_days / MAX_LIFESPAN_DAYS)

    def _compute_stability(self, decision: Decision) -> float:
        """
        Measures how stable a decision has been since adoption.

        Churn = number of DecisionVersion records beyond the first.
        A version count of 1 (never changed) → stability = 1.0.
        """
        version_count = len(decision.versions) if decision.versions else 1
        churn = max(0, version_count - 1)
        return max(0.0, 1.0 - (churn / CHURN_THRESHOLD))

    def _compute_impact(self, decision: Decision) -> float:
        """
        Measures the breadth of architectural impact.

        Counts distinct affected entities across capabilities, architectures, and
        services.  Saturates at IMPACT_SAT_ITEMS.
        """
        affected = (
            len(set(decision.affected_capabilities))
            + len(set(decision.affected_architectures))
            + len(set(decision.affected_services))
        )
        return min(1.0, affected / IMPACT_SAT_ITEMS)

    def _compute_adoption(self, decision: Decision) -> float:
        """
        Measures evidence density — how many unique data points confirm this decision.

        Supporting commits + supporting documents both contribute.
        """
        ev = decision.supporting_evidence
        commit_count = len(set(ev.supporting_commits))
        doc_count    = len(set(ev.supporting_documents))
        event_count  = len(set(ev.supporting_repository_events))

        # Commits are the primary signal; docs give a bonus
        commit_score = min(1.0, commit_count / ADOPTION_SAT_COMMITS)
        doc_bonus    = min(0.20, doc_count / ADOPTION_SAT_DOCS * 0.20)
        event_bonus  = min(0.10, event_count / 5 * 0.10)

        return min(1.0, commit_score + doc_bonus + event_bonus)

    def _compute_success_rate(self, decision: Decision) -> float:
        """
        Composite health proxy.

        Components:
            0.50 × confidence.score
            0.30 × status health weight
            0.20 × ADR confirmation bonus
        """
        confidence_component = 0.50 * decision.confidence.score

        status_health = _STATUS_HEALTH.get(decision.status, 0.1)
        status_component = 0.30 * status_health

        has_adr = bool(decision.supporting_evidence.supporting_documents)
        adr_component = 0.20 if has_adr else 0.05

        return min(1.0, confidence_component + status_component + adr_component)
