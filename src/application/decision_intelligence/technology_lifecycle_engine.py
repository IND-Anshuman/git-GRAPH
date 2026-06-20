"""
Phase 7C — TechnologyLifecycleEngine

Pairs TECHNOLOGY_ADOPTION and TECHNOLOGY_REMOVAL decisions by technology key
to build complete lifecycle records.

A lifecycle represents the full arc of a technology's adoption:

    ┌─────────────┐       ┌──────────────┐       ┌──────────────────┐
    │  INTRODUCED │──────▶│    ACTIVE    │──────▶│    REMOVED       │
    │  (Decision) │       │ (in commits) │       │  (Decision)       │
    └─────────────┘       └──────────────┘       └──────────────────┘

    Lifecycle fields:
        technology_key:       Normalised package name (e.g. "apache-kafka")
        display_name:         Human name (e.g. "Apache Kafka")
        adoption_decision_id: UUID of the TECHNOLOGY_ADOPTION decision
        removal_decision_id:  UUID of the TECHNOLOGY_REMOVAL decision (or None)
        adoption_commit:      First commit hash where adoption was detected
        removal_commit:       Last commit hash where removal was detected (or None)
        lifespan_days:        Estimated days between adoption and removal
        status:               "ACTIVE" | "RETIRED" | "PROPOSED"
        stability_index:      1.0 for single-version, lower for churned decisions
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from .decision import Decision
from .decision_type import DecisionType
from .decision_status import DecisionStatus

logger = logging.getLogger(__name__)


@dataclass
class TechnologyLifecycle:
    """Represents the complete lifecycle of a technology in a repository."""

    technology_key: str
    display_name: str
    adoption_decision_id: UUID
    removal_decision_id: Optional[UUID]
    adoption_commit: str
    removal_commit: Optional[str]
    repository_id: str
    status: str                         # "ACTIVE" | "RETIRED" | "PROPOSED"
    stability_index: float              # [0.0, 1.0] — inverse of version churn
    lifespan_days: Optional[int]        # None if still active
    adoption_decision_name: str         # Human-readable label
    removal_decision_name: Optional[str]

    # Evidence provenance
    supporting_commits: List[str] = field(default_factory=list)
    supporting_documents: List[str] = field(default_factory=list)


def _extract_tech_key_from_name(name: str) -> str:
    """
    Extract a normalised technology key from a decision name.

    Examples:
        "Adopt Apache Kafka"       → "apache-kafka"
        "Remove Redis"             → "redis"
        "Adopt AI: OpenAI API"     → "openai-api"
    """
    # Strip known prefixes
    prefixes = ["adopt ai:", "adopt infrastructure:", "adopt:", "adopt", "remove:", "remove",
                "enforce security:", "create capability:", "change ownership:"]
    lower = name.lower().strip()
    for p in prefixes:
        if lower.startswith(p):
            lower = lower[len(p):].strip()
            break
    # Normalise: lowercase, collapse whitespace, replace spaces with dashes
    key = re.sub(r"\s+", "-", lower.strip())
    key = re.sub(r"[^a-z0-9\-]", "", key)
    return key


class TechnologyLifecycleEngine:
    """
    Pairs TECHNOLOGY_ADOPTION and TECHNOLOGY_REMOVAL decisions to build
    complete technology lifecycle records.

    Usage::

        engine = TechnologyLifecycleEngine()
        lifecycles = engine.detect_lifecycles(decisions)
    """

    def detect_lifecycles(self, decisions: List[Decision]) -> List[TechnologyLifecycle]:
        """
        Scan decisions and pair adoptions with removals by technology key.

        Algorithm:
            1. Extract a normalised technology_key from each decision's name.
            2. Partition into: adoptions (TECHNOLOGY_ADOPTION, AI_ADOPTION, INFRASTRUCTURE)
               and removals (TECHNOLOGY_REMOVAL).
            3. For each adoption, find a matching removal by technology_key.
            4. Compute lifecycle status and stability_index.
        """
        if not decisions:
            return []

        # Partition decisions
        adoptions: Dict[str, Decision] = {}
        removals: Dict[str, Decision] = {}

        for decision in decisions:
            if decision.decision_type in (
                DecisionType.TECHNOLOGY_ADOPTION,
                DecisionType.AI_ADOPTION,
                DecisionType.INFRASTRUCTURE,
            ):
                tech_key = _extract_tech_key_from_name(decision.name)
                # Keep the earliest adoption if duplicates exist
                if tech_key not in adoptions:
                    adoptions[tech_key] = decision
                else:
                    existing = adoptions[tech_key]
                    if decision.created_at < existing.created_at:
                        adoptions[tech_key] = decision

            elif decision.decision_type == DecisionType.TECHNOLOGY_REMOVAL:
                tech_key = _extract_tech_key_from_name(decision.name)
                if tech_key not in removals:
                    removals[tech_key] = decision

        # Build lifecycle records
        lifecycles: List[TechnologyLifecycle] = []

        for tech_key, adoption in adoptions.items():
            removal = removals.get(tech_key)
            lifecycle = self._build_lifecycle(tech_key, adoption, removal)
            lifecycles.append(lifecycle)

        # Orphan removals (removal without a matching adoption — unusual but possible)
        for tech_key, removal in removals.items():
            if tech_key not in adoptions:
                orphan = TechnologyLifecycle(
                    technology_key=tech_key,
                    display_name=removal.name,
                    adoption_decision_id=removal.id,  # proxy
                    removal_decision_id=removal.id,
                    adoption_commit=removal.first_seen_commit,
                    removal_commit=removal.last_seen_commit,
                    repository_id=removal.repository_id,
                    status="RETIRED",
                    stability_index=1.0,
                    lifespan_days=None,
                    adoption_decision_name=removal.name,
                    removal_decision_name=removal.name,
                    supporting_commits=removal.supporting_evidence.supporting_commits,
                    supporting_documents=removal.supporting_evidence.supporting_documents,
                )
                lifecycles.append(orphan)

        logger.info(
            "TechnologyLifecycleEngine: detected %d lifecycle(s) "
            "(%d adoptions, %d removals, %d paired)",
            len(lifecycles),
            len(adoptions),
            len(removals),
            sum(1 for lc in lifecycles if lc.removal_decision_id is not None),
        )
        return lifecycles

    # ─────────────────────────────────────────────────────────────────────────
    #  Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _build_lifecycle(
        self,
        tech_key: str,
        adoption: Decision,
        removal: Optional[Decision],
    ) -> TechnologyLifecycle:
        """Build a TechnologyLifecycle from an adoption and optional removal."""

        # Compute stability_index: inverse of version churn
        version_count = max(1, len(adoption.versions))
        # If there's a removal, it adds 1 version of churn
        effective_versions = version_count + (1 if removal else 0)
        stability_index = max(0.0, min(1.0, 1.0 - ((effective_versions - 1) / 5.0)))

        # Determine status
        if removal is not None:
            status = "RETIRED"
        elif adoption.status == DecisionStatus.PROPOSED:
            status = "PROPOSED"
        elif adoption.status in (DecisionStatus.DEPRECATED, DecisionStatus.REVERTED):
            status = "RETIRED"
        else:
            status = "ACTIVE"

        # Estimate lifespan
        lifespan_days: Optional[int] = None
        if removal is not None and adoption.created_at and removal.created_at:
            adopt_dt = _ensure_tz(adoption.created_at)
            remove_dt = _ensure_tz(removal.created_at)
            delta = remove_dt - adopt_dt
            lifespan_days = max(0, delta.days)

        # Merge evidence
        all_commits = list(
            set(adoption.supporting_evidence.supporting_commits)
            | set(removal.supporting_evidence.supporting_commits if removal else [])
        )
        all_docs = list(
            set(adoption.supporting_evidence.supporting_documents)
            | set(removal.supporting_evidence.supporting_documents if removal else [])
        )

        return TechnologyLifecycle(
            technology_key=tech_key,
            display_name=_extract_display_name(adoption.name),
            adoption_decision_id=adoption.id,
            removal_decision_id=removal.id if removal else None,
            adoption_commit=adoption.first_seen_commit,
            removal_commit=removal.last_seen_commit if removal else None,
            repository_id=adoption.repository_id,
            status=status,
            stability_index=round(stability_index, 4),
            lifespan_days=lifespan_days,
            adoption_decision_name=adoption.name,
            removal_decision_name=removal.name if removal else None,
            supporting_commits=all_commits[:20],
            supporting_documents=all_docs[:10],
        )

    def get_retired_technologies(
        self, lifecycles: List[TechnologyLifecycle]
    ) -> List[TechnologyLifecycle]:
        """Filter to only retired / removed technologies."""
        return [lc for lc in lifecycles if lc.status == "RETIRED"]

    def get_active_technologies(
        self, lifecycles: List[TechnologyLifecycle]
    ) -> List[TechnologyLifecycle]:
        """Filter to only currently active technologies."""
        return [lc for lc in lifecycles if lc.status == "ACTIVE"]

    def get_unstable_technologies(
        self, lifecycles: List[TechnologyLifecycle], threshold: float = 0.5
    ) -> List[TechnologyLifecycle]:
        """Filter to technologies with stability_index below threshold."""
        return [lc for lc in lifecycles if lc.stability_index < threshold]


def _extract_display_name(decision_name: str) -> str:
    """Extract the human-readable technology name from a decision name."""
    prefixes = ["adopt ai: ", "adopt infrastructure: ", "adopt: ", "adopt ",
                "remove: ", "remove ", "enforce security: "]
    lower = decision_name.lower()
    for p in prefixes:
        if lower.startswith(p):
            remainder = decision_name[len(p):]
            return remainder.strip().title()
    return decision_name.strip()


def _ensure_tz(dt: Optional[datetime]) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
