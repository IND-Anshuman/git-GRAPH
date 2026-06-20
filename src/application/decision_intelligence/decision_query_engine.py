"""
Phase 7C — DecisionQueryEngine

The persistence-layer query facade for the Decision Intelligence Layer.

Provides structured access to stored decisions, versions, conflicts, fitness
records, intents, and causal relationships from the SQLAlchemy Unit of Work.

All queries:
    - Return domain objects (not ORM models) wherever possible, or raw ORM
      models when the caller is the API layer (for schema serialisation).
    - Accept typed parameters.
    - Are filtered, sorted, and paginated to be index-friendly.
    - Log query performance metadata at DEBUG level.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from .decision_type import DecisionType
from .decision_status import DecisionStatus

logger = logging.getLogger(__name__)


class DecisionQueryEngine:
    """
    Façade over the Unit of Work for all Decision Intelligence reads.

    Injected with a UoW instance (not a factory) to align with the existing
    platform pattern where the UoW is opened by the calling route/use-case.

    Usage::

        engine = DecisionQueryEngine(uow)
        decisions = engine.get_decisions_by_type(repository_id, DecisionType.TECHNOLOGY_ADOPTION)
    """

    def __init__(self, uow: Any) -> None:
        self._uow = uow

    # ─────────────────────────────────────────────────────────────────────────
    #  Decision queries
    # ─────────────────────────────────────────────────────────────────────────

    def get_all_decisions(self, repository_id: str) -> List[Any]:
        """Return all decisions for a repository, ordered by created_at desc."""
        with self._uow:
            rows = self._uow.decisions.get_by_repository_id(repository_id)
            logger.debug(
                "DecisionQueryEngine.get_all_decisions: repo=%s → %d rows",
                repository_id, len(rows),
            )
            return rows

    def get_decisions_by_type(
        self,
        repository_id: str,
        decision_type: DecisionType,
    ) -> List[Any]:
        """Return decisions filtered by type for a given repository."""
        with self._uow:
            all_rows = self._uow.decisions.get_by_repository_id(repository_id)
            filtered = [
                r for r in all_rows
                if r.decision_type == decision_type.value
            ]
            logger.debug(
                "DecisionQueryEngine.get_decisions_by_type: repo=%s type=%s → %d rows",
                repository_id, decision_type.value, len(filtered),
            )
            return filtered

    def get_decisions_by_status(
        self,
        repository_id: str,
        status: DecisionStatus,
    ) -> List[Any]:
        """Return decisions filtered by status."""
        with self._uow:
            all_rows = self._uow.decisions.get_by_repository_id(repository_id)
            filtered = [r for r in all_rows if r.status == status.value]
            return filtered

    def get_decision_by_id(self, decision_id: str) -> Optional[Any]:
        """Return a single decision by its string UUID."""
        with self._uow:
            row = self._uow.decisions.get_by_id(decision_id)
            return row

    def get_decision_history(self, repository_id: str) -> List[Any]:
        """
        Return decisions ordered chronologically (by created_at ascending).

        This is the full history view — suitable for timeline reconstruction.
        """
        with self._uow:
            rows = self._uow.decisions.get_by_repository_id(repository_id)
            sorted_rows = sorted(rows, key=lambda r: r.created_at or datetime.min)
            return sorted_rows

    def get_active_decisions(self, repository_id: str) -> List[Any]:
        """Return only ACTIVE decisions — the current decision baseline."""
        return self.get_decisions_by_status(repository_id, DecisionStatus.ACTIVE)

    def search_decisions(
        self,
        repository_id: str,
        query: str,
        decision_type: Optional[DecisionType] = None,
        status: Optional[DecisionStatus] = None,
        min_confidence: float = 0.0,
    ) -> List[Any]:
        """
        Full-text search over decision names and descriptions with optional filters.

        Args:
            repository_id:  Target repository.
            query:          Substring to search in name/description (case-insensitive).
            decision_type:  Optional type filter.
            status:         Optional status filter.
            min_confidence: Minimum confidence_score threshold (default 0.0).
        """
        with self._uow:
            all_rows = self._uow.decisions.get_by_repository_id(repository_id)
            q_lower = query.strip().lower()
            results = []
            for r in all_rows:
                if q_lower and q_lower not in (r.name or "").lower() and \
                   q_lower not in (r.description or "").lower():
                    continue
                if decision_type and r.decision_type != decision_type.value:
                    continue
                if status and r.status != status.value:
                    continue
                if min_confidence and (r.confidence_score or 0.0) < min_confidence:
                    continue
                results.append(r)
            return results

    # ─────────────────────────────────────────────────────────────────────────
    #  Decision Version queries
    # ─────────────────────────────────────────────────────────────────────────

    def get_decision_versions(self, decision_id: str) -> List[Any]:
        """Return all versions for a decision, ordered by version number ascending."""
        with self._uow:
            all_versions = self._uow.decision_versions.get_by_decision_id(decision_id)
            return sorted(all_versions, key=lambda v: v.version)

    # ─────────────────────────────────────────────────────────────────────────
    #  Conflict queries
    # ─────────────────────────────────────────────────────────────────────────

    def get_decision_conflicts(self, decision_id: str) -> List[Any]:
        """Return all conflicts involving this decision (as decision_a or decision_b)."""
        with self._uow:
            return self._uow.decision_conflicts.get_by_decision_id(decision_id)

    def get_all_conflicts(self, repository_id: str) -> List[Any]:
        """Return all conflicts across all decisions in a repository."""
        with self._uow:
            return self._uow.decision_conflicts.get_by_repository_id(repository_id)

    # ─────────────────────────────────────────────────────────────────────────
    #  Fitness queries
    # ─────────────────────────────────────────────────────────────────────────

    def get_decision_fitness(self, decision_id: str) -> Optional[Any]:
        """Return the latest fitness record for a decision."""
        with self._uow:
            return self._uow.decision_fitness.get_by_decision_id(decision_id)

    def get_low_fitness_decisions(
        self,
        repository_id: str,
        threshold: float = 0.4,
    ) -> List[Any]:
        """
        Return decisions whose overall_fitness is below threshold.

        Useful for surfacing decisions that need attention or review.
        """
        with self._uow:
            all_rows = self._uow.decisions.get_by_repository_id(repository_id)
            low_fitness = []
            for decision in all_rows:
                fitness = self._uow.decision_fitness.get_by_decision_id(str(decision.id))
                if fitness and (fitness.overall_fitness or 1.0) < threshold:
                    low_fitness.append(decision)
            return low_fitness

    # ─────────────────────────────────────────────────────────────────────────
    #  Intent queries
    # ─────────────────────────────────────────────────────────────────────────

    def get_intents(self, repository_id: str) -> List[Any]:
        """Return all intents for a repository."""
        with self._uow:
            return self._uow.intents.get_by_repository_id(repository_id)

    def get_intent_by_id(self, intent_id: str) -> Optional[Any]:
        """Return a single intent by its string UUID."""
        with self._uow:
            return self._uow.intents.get_by_id(intent_id)

    # ─────────────────────────────────────────────────────────────────────────
    #  Causal relationship queries
    # ─────────────────────────────────────────────────────────────────────────

    def get_causal_chains(self, repository_id: str) -> List[Any]:
        """Return all causal relationships grouped by chain_id for a repository."""
        with self._uow:
            return self._uow.causal_relationships.get_by_repository_id(repository_id)

    # ─────────────────────────────────────────────────────────────────────────
    #  Summary / analytics queries
    # ─────────────────────────────────────────────────────────────────────────

    def get_decision_summary(self, repository_id: str) -> Dict[str, Any]:
        """
        Return a high-level summary of the decision landscape for a repository.

        Useful for dashboard / portfolio views.
        """
        with self._uow:
            all_decisions = self._uow.decisions.get_by_repository_id(repository_id)
            intents = self._uow.intents.get_by_repository_id(repository_id)

            by_type: Dict[str, int] = {}
            by_status: Dict[str, int] = {}
            confidence_sum = 0.0
            confidence_count = 0

            for d in all_decisions:
                by_type[d.decision_type] = by_type.get(d.decision_type, 0) + 1
                by_status[d.status] = by_status.get(d.status, 0) + 1
                if d.confidence_score is not None:
                    confidence_sum += d.confidence_score
                    confidence_count += 1

            avg_confidence = (
                round(confidence_sum / confidence_count, 4)
                if confidence_count > 0 else 0.0
            )

            return {
                "repository_id": repository_id,
                "total_decisions": len(all_decisions),
                "total_intents": len(intents),
                "by_type": by_type,
                "by_status": by_status,
                "average_confidence": avg_confidence,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
