"""
Phase 7C — SQLAlchemy Repository Implementations for Decision Intelligence Layer.

Each repository extends the generic SQLAlchemyRepository[T] base and adds
domain-specific query methods required by the DecisionQueryEngine and API layer.

All methods:
    - Use indexed columns (repository_id, decision_id) to avoid full-table scans.
    - Return List[T] or Optional[T] — never raw SQLAlchemy Row objects.
    - Are typed for IDE / type-checker support.
"""

from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session

from .base import SQLAlchemyRepository
from src.infrastructure.persistence.models.decision_models import (
    SADecision,
    SADecisionVersion,
    SADecisionEvidence,
    SADecisionImpact,
    SADecisionImpactTimeline,
    SADecisionDependency,
    SADecisionConflict,
    SADecisionFitness,
    SADecisionSnapshot,
    SAIntent,
    SAIntentRelationship,
    SARepositoryMemoryEvent,
    SACausalRelationship,
)


# ─── Decision ─────────────────────────────────────────────────────────────────

class SADecisionRepository(SQLAlchemyRepository[SADecision]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SADecision)

    def get_by_repository_id(self, repository_id: str) -> List[SADecision]:
        """Return all decisions for a repository, newest first."""
        return (
            self.session.query(SADecision)
            .filter(SADecision.repository_id == repository_id)
            .order_by(SADecision.created_at.desc())
            .all()
        )

    def get_by_id(self, decision_id: str) -> Optional[SADecision]:
        return self.session.get(SADecision, decision_id)

    def get_by_type(self, repository_id: str, decision_type: str) -> List[SADecision]:
        return (
            self.session.query(SADecision)
            .filter(
                SADecision.repository_id == repository_id,
                SADecision.decision_type == decision_type,
            )
            .all()
        )

    def get_by_status(self, repository_id: str, status: str) -> List[SADecision]:
        return (
            self.session.query(SADecision)
            .filter(
                SADecision.repository_id == repository_id,
                SADecision.status == status,
            )
            .order_by(SADecision.created_at.desc())
            .all()
        )

    def get_above_confidence(
        self, repository_id: str, min_confidence: float
    ) -> List[SADecision]:
        return (
            self.session.query(SADecision)
            .filter(
                SADecision.repository_id == repository_id,
                SADecision.confidence_score >= min_confidence,
            )
            .all()
        )


# ─── Decision Version ─────────────────────────────────────────────────────────

class SADecisionVersionRepository(SQLAlchemyRepository[SADecisionVersion]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SADecisionVersion)

    def get_by_decision_id(self, decision_id: str) -> List[SADecisionVersion]:
        """Return all versions for a decision ordered ascending by version number."""
        return (
            self.session.query(SADecisionVersion)
            .filter(SADecisionVersion.decision_id == decision_id)
            .order_by(SADecisionVersion.version.asc())
            .all()
        )

    def get_latest(self, decision_id: str) -> Optional[SADecisionVersion]:
        return (
            self.session.query(SADecisionVersion)
            .filter(SADecisionVersion.decision_id == decision_id)
            .order_by(SADecisionVersion.version.desc())
            .first()
        )


# ─── Decision Evidence ────────────────────────────────────────────────────────

class SADecisionEvidenceRepository(SQLAlchemyRepository[SADecisionEvidence]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SADecisionEvidence)

    def get_by_decision_id(self, decision_id: str) -> Optional[SADecisionEvidence]:
        return (
            self.session.query(SADecisionEvidence)
            .filter(SADecisionEvidence.decision_id == decision_id)
            .first()
        )


# ─── Decision Impact ──────────────────────────────────────────────────────────

class SADecisionImpactRepository(SQLAlchemyRepository[SADecisionImpact]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SADecisionImpact)

    def get_by_decision_id(self, decision_id: str) -> Optional[SADecisionImpact]:
        return (
            self.session.query(SADecisionImpact)
            .filter(SADecisionImpact.decision_id == decision_id)
            .first()
        )


# ─── Decision Impact Timeline ─────────────────────────────────────────────────

class SADecisionImpactTimelineRepository(SQLAlchemyRepository[SADecisionImpactTimeline]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SADecisionImpactTimeline)

    def get_by_decision_id(self, decision_id: str) -> Optional[SADecisionImpactTimeline]:
        return (
            self.session.query(SADecisionImpactTimeline)
            .filter(SADecisionImpactTimeline.decision_id == decision_id)
            .first()
        )


# ─── Decision Dependency ──────────────────────────────────────────────────────

class SADecisionDependencyRepository(SQLAlchemyRepository[SADecisionDependency]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SADecisionDependency)

    def get_by_source(self, source_decision_id: str) -> List[SADecisionDependency]:
        return (
            self.session.query(SADecisionDependency)
            .filter(SADecisionDependency.source_decision_id == source_decision_id)
            .all()
        )

    def get_by_target(self, target_decision_id: str) -> List[SADecisionDependency]:
        return (
            self.session.query(SADecisionDependency)
            .filter(SADecisionDependency.target_decision_id == target_decision_id)
            .all()
        )


# ─── Decision Conflict ────────────────────────────────────────────────────────

class SADecisionConflictRepository(SQLAlchemyRepository[SADecisionConflict]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SADecisionConflict)

    def get_by_decision_id(self, decision_id: str) -> List[SADecisionConflict]:
        """Return all conflicts where this decision is party A or party B."""
        return (
            self.session.query(SADecisionConflict)
            .filter(
                (SADecisionConflict.decision_a_id == decision_id)
                | (SADecisionConflict.decision_b_id == decision_id)
            )
            .order_by(SADecisionConflict.detected_at.desc())
            .all()
        )

    def get_by_repository_id(self, repository_id: str) -> List[SADecisionConflict]:
        """
        Return all conflicts for a repository by joining through SADecision.
        Uses a subquery for index efficiency.
        """
        decision_ids_subq = (
            self.session.query(SADecision.id)
            .filter(SADecision.repository_id == repository_id)
            .subquery()
        )
        return (
            self.session.query(SADecisionConflict)
            .filter(
                (SADecisionConflict.decision_a_id.in_(decision_ids_subq))
                | (SADecisionConflict.decision_b_id.in_(decision_ids_subq))
            )
            .all()
        )


# ─── Decision Fitness ─────────────────────────────────────────────────────────

class SADecisionFitnessRepository(SQLAlchemyRepository[SADecisionFitness]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SADecisionFitness)

    def get_by_decision_id(self, decision_id: str) -> Optional[SADecisionFitness]:
        """Return the latest fitness record for a decision."""
        return (
            self.session.query(SADecisionFitness)
            .filter(SADecisionFitness.decision_id == decision_id)
            .order_by(SADecisionFitness.evaluated_at.desc())
            .first()
        )

    def get_below_threshold(
        self, repository_id: str, threshold: float
    ) -> List[SADecisionFitness]:
        """Return fitness records for a repository where overall_fitness < threshold."""
        decision_ids_subq = (
            self.session.query(SADecision.id)
            .filter(SADecision.repository_id == repository_id)
            .subquery()
        )
        return (
            self.session.query(SADecisionFitness)
            .filter(
                SADecisionFitness.decision_id.in_(decision_ids_subq),
                SADecisionFitness.overall_fitness < threshold,
            )
            .all()
        )


# ─── Decision Snapshot ────────────────────────────────────────────────────────

class SADecisionSnapshotRepository(SQLAlchemyRepository[SADecisionSnapshot]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SADecisionSnapshot)

    def get_by_repository_id(self, repository_id: str) -> List[SADecisionSnapshot]:
        return (
            self.session.query(SADecisionSnapshot)
            .filter(SADecisionSnapshot.repository_id == repository_id)
            .order_by(SADecisionSnapshot.generated_at.asc())
            .all()
        )

    def get_by_commit(
        self, repository_id: str, commit_hash: str
    ) -> Optional[SADecisionSnapshot]:
        return (
            self.session.query(SADecisionSnapshot)
            .filter(
                SADecisionSnapshot.repository_id == repository_id,
                SADecisionSnapshot.commit_hash == commit_hash,
            )
            .first()
        )


# ─── Intent ───────────────────────────────────────────────────────────────────

class SAIntentRepository(SQLAlchemyRepository[SAIntent]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SAIntent)

    def get_by_repository_id(self, repository_id: str) -> List[SAIntent]:
        return (
            self.session.query(SAIntent)
            .filter(SAIntent.repository_id == repository_id)
            .order_by(SAIntent.first_seen_at.asc())
            .all()
        )

    def get_by_id(self, intent_id: str) -> Optional[SAIntent]:
        return self.session.get(SAIntent, intent_id)

    def get_by_type(self, repository_id: str, intent_type: str) -> List[SAIntent]:
        return (
            self.session.query(SAIntent)
            .filter(
                SAIntent.repository_id == repository_id,
                SAIntent.intent_type == intent_type,
            )
            .all()
        )


# ─── Intent Relationship ──────────────────────────────────────────────────────

class SAIntentRelationshipRepository(SQLAlchemyRepository[SAIntentRelationship]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SAIntentRelationship)

    def get_by_intent_id(self, intent_id: str) -> List[SAIntentRelationship]:
        return (
            self.session.query(SAIntentRelationship)
            .filter(SAIntentRelationship.intent_id == intent_id)
            .all()
        )

    def get_by_decision_id(self, decision_id: str) -> List[SAIntentRelationship]:
        return (
            self.session.query(SAIntentRelationship)
            .filter(SAIntentRelationship.decision_id == decision_id)
            .all()
        )


# ─── Repository Memory Event ──────────────────────────────────────────────────

class SARepositoryMemoryEventRepository(SQLAlchemyRepository[SARepositoryMemoryEvent]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SARepositoryMemoryEvent)

    def get_by_repository_id(self, repository_id: str) -> List[SARepositoryMemoryEvent]:
        return (
            self.session.query(SARepositoryMemoryEvent)
            .filter(SARepositoryMemoryEvent.repository_id == repository_id)
            .order_by(SARepositoryMemoryEvent.occurred_at.asc())
            .all()
        )

    def get_by_event_type(
        self, repository_id: str, event_type: str
    ) -> List[SARepositoryMemoryEvent]:
        return (
            self.session.query(SARepositoryMemoryEvent)
            .filter(
                SARepositoryMemoryEvent.repository_id == repository_id,
                SARepositoryMemoryEvent.event_type == event_type,
            )
            .order_by(SARepositoryMemoryEvent.occurred_at.asc())
            .all()
        )


# ─── Causal Relationship ──────────────────────────────────────────────────────

class SACausalRelationshipRepository(SQLAlchemyRepository[SACausalRelationship]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SACausalRelationship)

    def get_by_repository_id(self, repository_id: str) -> List[SACausalRelationship]:
        return (
            self.session.query(SACausalRelationship)
            .filter(SACausalRelationship.repository_id == repository_id)
            .all()
        )

    def get_by_chain_id(self, chain_id: str) -> List[SACausalRelationship]:
        return (
            self.session.query(SACausalRelationship)
            .filter(SACausalRelationship.chain_id == chain_id)
            .all()
        )

    def get_by_cause_id(self, cause_id: str) -> List[SACausalRelationship]:
        return (
            self.session.query(SACausalRelationship)
            .filter(SACausalRelationship.cause_id == cause_id)
            .all()
        )

    def get_by_effect_id(self, effect_id: str) -> List[SACausalRelationship]:
        return (
            self.session.query(SACausalRelationship)
            .filter(SACausalRelationship.effect_id == effect_id)
            .all()
        )
