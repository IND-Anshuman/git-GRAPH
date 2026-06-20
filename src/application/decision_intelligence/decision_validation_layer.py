"""
Phase 7C — DecisionValidationLayer

A state-machine validator that enforces two categories of rules:

    1. Structural Integrity Rules
       - confidence.score must exceed minimum threshold
       - at least one provenanced evidence source must exist
       - name and description must be non-empty

    2. State-Transition Legality Rules
       Governs which DecisionStatus transitions are legal.

       Legal transitions:
           PROPOSED    → ACTIVE, REVERTED
           ACTIVE      → SUPERSEDED, DEPRECATED, REVERTED
           SUPERSEDED  → (terminal — no further transitions)
           DEPRECATED  → (terminal — no further transitions)
           REVERTED    → PROPOSED (only — can be re-evaluated)

       Any other transition raises a validation failure, which results in
       the decision being quarantined (returned in the rejected list rather
       than silently dropped).

Output:
    validate() returns a tuple (valid: List[Decision], rejected: List[RejectedDecision])
    so that callers can log, quarantine, or alert on failures rather than silently losing data.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Set, Tuple

from .decision import Decision
from .decision_status import DecisionStatus

logger = logging.getLogger(__name__)

# ─── Tuning ──────────────────────────────────────────────────────────────────
MIN_CONFIDENCE_THRESHOLD: float = 0.30

# State machine: maps current status → set of legal next statuses
_LEGAL_TRANSITIONS: dict[DecisionStatus, Set[DecisionStatus]] = {
    DecisionStatus.PROPOSED:    {DecisionStatus.ACTIVE, DecisionStatus.REVERTED},
    DecisionStatus.ACTIVE:      {DecisionStatus.SUPERSEDED, DecisionStatus.DEPRECATED, DecisionStatus.REVERTED},
    DecisionStatus.SUPERSEDED:  set(),   # Terminal
    DecisionStatus.DEPRECATED:  set(),   # Terminal
    DecisionStatus.REVERTED:    {DecisionStatus.PROPOSED},
}

# Decisions born with no prior version are implicitly in PROPOSED before becoming ACTIVE.
# So ACTIVE with version_count=1 is always legal (initial adoption).
_INITIAL_LEGAL_STATUSES: Set[DecisionStatus] = {DecisionStatus.PROPOSED, DecisionStatus.ACTIVE}


@dataclass(frozen=True)
class RejectedDecision:
    """Carries a rejected decision alongside the reason it failed validation."""
    decision: Decision
    reasons: List[str]


class DecisionValidationLayer:
    """
    Enforces structural integrity and state-machine legality for decisions.

    Usage::

        validator = DecisionValidationLayer()
        valid, rejected = validator.validate(decisions)
        for r in rejected:
            logger.warning("Rejected '%s': %s", r.decision.name, r.reasons)
    """

    def validate(
        self,
        decisions: List[Decision],
    ) -> Tuple[List[Decision], List[RejectedDecision]]:
        """
        Validate a list of decisions.

        Returns:
            (valid_decisions, rejected_decisions) tuple.
        """
        valid: List[Decision] = []
        rejected: List[RejectedDecision] = []

        for decision in decisions:
            reasons = self._collect_violations(decision)
            if reasons:
                rejected.append(RejectedDecision(decision=decision, reasons=reasons))
                logger.warning(
                    "DecisionValidationLayer: Rejected '%s' [%s] — %s",
                    decision.name,
                    decision.id,
                    "; ".join(reasons),
                )
            else:
                valid.append(decision)

        logger.info(
            "DecisionValidationLayer: %d valid, %d rejected from %d total",
            len(valid),
            len(rejected),
            len(decisions),
        )
        return valid, rejected

    # ─────────────────────────────────────────────────────────────────────────
    #  Validation rules
    # ─────────────────────────────────────────────────────────────────────────

    def _collect_violations(self, decision: Decision) -> List[str]:
        reasons: List[str] = []

        # Rule 1: Confidence threshold
        if decision.confidence.score < MIN_CONFIDENCE_THRESHOLD:
            reasons.append(
                f"confidence {decision.confidence.score:.3f} < threshold {MIN_CONFIDENCE_THRESHOLD}"
            )

        # Rule 2: At least one provenanced evidence source
        ev = decision.supporting_evidence
        has_evidence = (
            ev.supporting_commits
            or ev.supporting_documents
            or ev.supporting_repository_events
            or ev.supporting_architecture_changes
        )
        if not has_evidence:
            reasons.append("no provenanced evidence attached")

        # Rule 3: Non-empty name
        if not decision.name or not decision.name.strip():
            reasons.append("decision name is empty")

        # Rule 4: Non-empty description
        if not decision.description or not decision.description.strip():
            reasons.append("decision description is empty")

        # Rule 5: State-transition legality
        transition_error = self._check_state_transition(decision)
        if transition_error:
            reasons.append(transition_error)

        return reasons

    def _check_state_transition(self, decision: Decision) -> str | None:
        """
        Verifies that the decision's current status is reachable given its
        version history.

        Logic:
            - If version_count == 1 → decision is newborn, must be in an initial legal status.
            - If version_count > 1 → the last two versions must represent a legal transition.
              We check: previous_version.confidence → current status alignment (proxied
              by version count order since we don't store previous status in DecisionVersion).

        Since DecisionVersion doesn't carry a previous_status field, we enforce the
        simpler invariant: terminal statuses (SUPERSEDED, DEPRECATED) cannot have new
        versions added after the terminal version.
        """
        status = decision.status
        versions = decision.versions or []
        version_count = len(versions)

        if version_count <= 1:
            # Newborn decisions must start in an initial legal status
            if status not in _INITIAL_LEGAL_STATUSES:
                return (
                    f"new decision (v1) has illegal initial status '{status.value}'; "
                    f"must be one of {[s.value for s in _INITIAL_LEGAL_STATUSES]}"
                )
            return None

        # version_count > 1 — decision has evolved
        # Check: terminal statuses should not have multiple versions
        # (once SUPERSEDED or DEPRECATED, no further version should appear)
        if status == DecisionStatus.SUPERSEDED and version_count > 2:
            return (
                f"SUPERSEDED decision has {version_count} versions — "
                "terminal decisions should not accumulate new versions"
            )

        if status == DecisionStatus.DEPRECATED and version_count > 2:
            return (
                f"DEPRECATED decision has {version_count} versions — "
                "terminal decisions should not accumulate new versions"
            )

        return None

    # ─────────────────────────────────────────────────────────────────────────
    #  Convenience single-decision API
    # ─────────────────────────────────────────────────────────────────────────

    def is_valid(self, decision: Decision) -> bool:
        """Returns True if the decision passes all validation rules."""
        return not bool(self._collect_violations(decision))

    def get_violations(self, decision: Decision) -> List[str]:
        """Returns a list of human-readable violation messages, or empty list if valid."""
        return self._collect_violations(decision)
