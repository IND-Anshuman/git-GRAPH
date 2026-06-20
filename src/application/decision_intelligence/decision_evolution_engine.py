"""
Phase 7C — DecisionEvolutionEngine

Builds a chronological timeline of decisions and detects evolution patterns:

    ┌─────────────────────────────────────────────────────────────┐
    │  Input:  List[Decision]  (sorted by first_seen_commit)      │
    │                                                             │
    │  Pipeline:                                                  │
    │    1. Sort decisions chronologically by first_seen_commit   │
    │       using DecisionVersion timestamps.                     │
    │    2. Assign each decision to time-windows (snapshots)      │
    │       anchored at each unique commit hash.                  │
    │    3. Build a DecisionTimeline with ordered snapshots.      │
    │    4. Scan the timeline for:                                │
    │         - Supersessions (A replaces B)                      │
    │         - Reversals (REVERTED decision re-appears ACTIVE)   │
    │         - Oscillations (status alternates > N times)        │
    │         - Longevity outliers (unusually short/long-lived)   │
    └─────────────────────────────────────────────────────────────┘

Pattern Detection:
    Supersession:   A decision becomes SUPERSEDED while another with the
                    same DecisionType appears ACTIVE in the same timeframe.

    Reversal:       A REVERTED decision regains ACTIVE status in a later
                    version snapshot.

    Oscillation:    A decision's status (across its versions) alternates
                    between ACTIVE and REVERTED more than OSCILLATION_THRESHOLD
                    times.

    Longevity Gap:  A decision was active for fewer than MIN_LONGEVITY_DAYS,
                    indicating a failed or exploratory adoption.
"""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .decision import Decision
from .decision_snapshot import DecisionSnapshot
from .decision_status import DecisionStatus
from .decision_timeline import DecisionTimeline

logger = logging.getLogger(__name__)

OSCILLATION_THRESHOLD: int = 2     # > 2 ACTIVE ↔ REVERTED flips = oscillation
MIN_LONGEVITY_DAYS: int = 7        # < 7 days = short-lived / failed experiment


class DecisionEvolutionEngine:
    """
    Builds chronological timelines and detects evolution patterns across
    a repository's decision history.

    Usage::

        engine = DecisionEvolutionEngine()
        timeline = engine.build_timeline(decisions)
        patterns = engine.detect_evolution_patterns(timeline, decisions)
    """

    # ─────────────────────────────────────────────────────────────────────────
    #  Timeline builder
    # ─────────────────────────────────────────────────────────────────────────

    def build_timeline(self, decisions: List[Decision]) -> DecisionTimeline:
        """
        Sorts decisions by first_seen_commit (using version timestamp as
        secondary key) and groups them into commit-anchored snapshots.

        Each snapshot represents the set of decisions that were ACTIVE at
        a particular commit hash.

        Returns:
            A :class:`DecisionTimeline` with ordered :class:`DecisionSnapshot` entries.
        """
        if not decisions:
            return DecisionTimeline(
                repository_id="unknown",
                first_commit="",
                last_commit="",
                snapshots=[],
            )

        repository_id = decisions[0].repository_id

        # Sort decisions chronologically using their earliest version timestamp,
        # falling back to created_at if no versions exist.
        def sort_key(d: Decision) -> datetime:
            if d.versions:
                earliest = min(
                    (v.generated_at for v in d.versions if v.generated_at is not None),
                    default=d.created_at,
                )
                return _ensure_tz(earliest) if earliest else _ensure_tz(d.created_at)
            return _ensure_tz(d.created_at)

        sorted_decisions = sorted(decisions, key=sort_key)

        # Group into commit-anchored snapshots
        # Each unique first_seen_commit becomes a snapshot boundary.
        commit_to_decision_ids: Dict[str, List[str]] = defaultdict(list)
        all_commits: List[str] = []

        for decision in sorted_decisions:
            commit = decision.first_seen_commit or decision.last_seen_commit
            if commit:
                commit_to_decision_ids[commit].append(str(decision.id))
                if commit not in all_commits:
                    all_commits.append(commit)

        # Also add last_seen_commit as a snapshot boundary (decisions may close here)
        for decision in sorted_decisions:
            last = decision.last_seen_commit
            if last and last not in all_commits:
                all_commits.append(last)

        # Build snapshots — each snapshot carries all decisions ACTIVE up to that commit
        snapshots: List[DecisionSnapshot] = []
        active_decision_ids: List[str] = []
        now = datetime.now(timezone.utc)

        for commit in all_commits:
            # Add decisions that first appeared at this commit
            for d_id in commit_to_decision_ids.get(commit, []):
                if d_id not in active_decision_ids:
                    active_decision_ids.append(d_id)

            # Remove decisions whose last_seen_commit was before this one
            # (They have been superseded/removed)
            commit_idx = all_commits.index(commit)
            still_active = []
            for d_id in active_decision_ids:
                decision = next((d for d in sorted_decisions if str(d.id) == d_id), None)
                if decision is None:
                    continue
                # Find index of last_seen_commit
                last = decision.last_seen_commit
                if last and last in all_commits:
                    last_idx = all_commits.index(last)
                    if last_idx < commit_idx:
                        continue  # This decision has passed its last_seen_commit
                still_active.append(d_id)
            active_decision_ids = still_active

            snapshot = DecisionSnapshot(
                snapshot_id=uuid.uuid4(),
                repository_id=repository_id,
                commit_hash=commit,
                decision_ids=list(active_decision_ids),
                generated_at=now,
            )
            snapshots.append(snapshot)

        first_commit = all_commits[0] if all_commits else ""
        last_commit = all_commits[-1] if all_commits else ""

        logger.info(
            "DecisionEvolutionEngine: built timeline with %d snapshots for repo '%s'",
            len(snapshots),
            repository_id,
        )

        return DecisionTimeline(
            repository_id=repository_id,
            first_commit=first_commit,
            last_commit=last_commit,
            snapshots=snapshots,
        )

    # ─────────────────────────────────────────────────────────────────────────
    #  Pattern detector
    # ─────────────────────────────────────────────────────────────────────────

    def detect_evolution_patterns(
        self,
        timeline: DecisionTimeline,
        decisions: Optional[List[Decision]] = None,
    ) -> Dict[str, Any]:
        """
        Scans a :class:`DecisionTimeline` for known evolution anti-patterns.

        Returns a dict with keys:
            reversals:      List of decision IDs whose status was REVERTED then re-ACTIVE.
            supersessions:  List of (superseded_id, replacement_type) pairs.
            oscillations:   List of decision IDs exhibiting ACTIVE↔REVERTED oscillation.
            short_lived:    List of decision IDs with age < MIN_LONGEVITY_DAYS.
            summary:        Human-readable summary string.
        """
        decisions = decisions or []
        decision_map: Dict[str, Decision] = {str(d.id): d for d in decisions}

        reversals = self._detect_reversals(decision_map)
        supersessions = self._detect_supersessions(decisions)
        oscillations = self._detect_oscillations(decision_map)
        short_lived = self._detect_short_lived(decisions)

        summary_parts = []
        if reversals:
            summary_parts.append(f"{len(reversals)} reversal(s)")
        if supersessions:
            summary_parts.append(f"{len(supersessions)} supersession(s)")
        if oscillations:
            summary_parts.append(f"{len(oscillations)} oscillation(s)")
        if short_lived:
            summary_parts.append(f"{len(short_lived)} short-lived adoption(s)")

        summary = (
            "Evolution patterns detected: " + ", ".join(summary_parts)
            if summary_parts
            else "No significant evolution patterns detected."
        )

        logger.info("DecisionEvolutionEngine: %s", summary)

        return {
            "reversals": reversals,
            "supersessions": supersessions,
            "oscillations": oscillations,
            "short_lived": short_lived,
            "summary": summary,
        }

    # ─────────────────────────────────────────────────────────────────────────
    #  Pattern sub-detectors
    # ─────────────────────────────────────────────────────────────────────────

    def _detect_reversals(self, decision_map: Dict[str, Decision]) -> List[str]:
        """
        A reversal occurs when a decision has a version with confidence that
        implies a REVERTED state but ends up ACTIVE again.

        Since DecisionVersion doesn't carry status, we use a heuristic:
            - A REVERTED decision (status == REVERTED) that also has
              last_seen_commit != first_seen_commit was once active and then
              reverted — it's a reversal candidate.
            - A PROPOSED decision that was previously REVERTED (inferred from
              multiple versions) is also flagged.
        """
        reversals = []
        for d_id, decision in decision_map.items():
            if decision.status == DecisionStatus.REVERTED:
                # Was it ever active? More than 1 version means it evolved.
                if len(decision.versions) > 1:
                    reversals.append(d_id)
            if decision.status == DecisionStatus.PROPOSED and len(decision.versions) > 2:
                # Multiple re-evaluations — was likely reverted before
                reversals.append(d_id)
        return reversals

    def _detect_supersessions(self, decisions: List[Decision]) -> List[Dict[str, str]]:
        """
        Detects when one decision type supersedes a prior one of the same type.

        A supersession is flagged when:
            - A decision has status SUPERSEDED, AND
            - Another decision of the same DecisionType is ACTIVE
        """
        supersessions = []
        superseded = [d for d in decisions if d.status == DecisionStatus.SUPERSEDED]
        active = [d for d in decisions if d.status == DecisionStatus.ACTIVE]

        for s_decision in superseded:
            # Find an active decision of the same type that appeared after
            for a_decision in active:
                if a_decision.decision_type == s_decision.decision_type:
                    supersessions.append({
                        "superseded_id": str(s_decision.id),
                        "superseded_name": s_decision.name,
                        "replacement_id": str(a_decision.id),
                        "replacement_name": a_decision.name,
                        "decision_type": s_decision.decision_type.value,
                    })
        return supersessions

    def _detect_oscillations(self, decision_map: Dict[str, Decision]) -> List[str]:
        """
        Oscillation: a decision's version confidence drops and rises repeatedly,
        suggesting indecision or repeated reversal.

        Heuristic: if a decision has ≥ OSCILLATION_THRESHOLD+1 versions and the
        confidence scores across versions form a decreasing-then-increasing pattern
        (zigzag), it's flagged as oscillating.
        """
        oscillations = []
        for d_id, decision in decision_map.items():
            versions = sorted(
                [v for v in decision.versions if v.generated_at is not None],
                key=lambda v: v.generated_at,
            )
            if len(versions) <= OSCILLATION_THRESHOLD:
                continue

            confidences = [v.confidence for v in versions]
            direction_changes = 0
            for i in range(1, len(confidences) - 1):
                prev_up = confidences[i] > confidences[i - 1]
                next_up = confidences[i + 1] > confidences[i]
                if prev_up != next_up:
                    direction_changes += 1

            if direction_changes >= OSCILLATION_THRESHOLD:
                oscillations.append(d_id)

        return oscillations

    def _detect_short_lived(self, decisions: List[Decision]) -> List[str]:
        """
        Flags decisions whose lifespan (last_seen_commit_date - first_seen_commit_date)
        is below MIN_LONGEVITY_DAYS.

        Since we only have commit hashes (not dates), we proxy using version timestamps.
        """
        short_lived = []
        for decision in decisions:
            versions_with_dates = [v for v in decision.versions if v.generated_at is not None]
            if len(versions_with_dates) < 2:
                continue

            sorted_versions = sorted(versions_with_dates, key=lambda v: v.generated_at)
            first_date = _ensure_tz(sorted_versions[0].generated_at)
            last_date = _ensure_tz(sorted_versions[-1].generated_at)

            age_days = (last_date - first_date).days
            if 0 <= age_days < MIN_LONGEVITY_DAYS:
                short_lived.append(str(decision.id))

        return short_lived


def _ensure_tz(dt: Optional[datetime]) -> datetime:
    """Ensure a datetime is timezone-aware (UTC fallback)."""
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
