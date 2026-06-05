"""Application service for querying logic evolution history and behavior drift analytics."""

from typing import Any, Callable, Dict, List, Optional
import uuid

from src.domain.entities.behavior_drift import BehaviorDrift
from src.domain.entities.logic_transition import LogicTransition
from src.domain.entities.logic_version import LogicVersion
from src.domain.enums.drift_category import DriftCategory
from src.domain.value_objects.repository_id import RepositoryId
from src.application.ports.unit_of_work import IUnitOfWork


class LogicEvolutionService:
    """Provides high-level queries for logic signatures, transitions, and behavior drift."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def get_signature_history(self, signature_id: uuid.UUID) -> List[LogicVersion]:
        """Get the chronological version history of a LogicSignature."""
        with self._uow_factory() as uow:
            versions = uow.logic_versions.list_by_signature(signature_id)
        versions.sort(key=lambda x: x.version_ordinal)
        return versions

    def get_signature_transitions(
        self, signature_id: uuid.UUID
    ) -> List[LogicTransition]:
        """Get all behavioral transitions between versions of a LogicSignature."""
        with self._uow_factory() as uow:
            return uow.logic_transitions.list_by_signature(signature_id)

    def get_behavior_drift_timeline(
        self,
        repository_id: RepositoryId,
        category: Optional[DriftCategory] = None,
    ) -> List[BehaviorDrift]:
        """Get behavior drift timeline for a repository, optionally filtered by category."""
        with self._uow_factory() as uow:
            if category:
                return uow.behavior_drift.list_by_drift_category(
                    repository_id, category
                )
            # If no category, we can list all drift records by getting all transitions and querying drift
            signatures = uow.logic_signatures.list_by_repository(
                repository_id
            )
            drifts = []
            for sig in signatures:
                transitions = uow.logic_transitions.list_by_signature(sig.id)
                for t in transitions:
                    drift = uow.behavior_drift.get_by_transition(t.id)
                    if drift:
                        drifts.append(drift)
        # Sort by computation time or transition version info
        drifts.sort(key=lambda x: x.computed_at, reverse=True)
        return drifts

    def get_security_boundary_crossings(
        self, repository_id: RepositoryId
    ) -> List[BehaviorDrift]:
        """Get all drifts that crossed a security boundary in the repository."""
        with self._uow_factory() as uow:
            return uow.behavior_drift.list_by_security_boundary_crossed(
                repository_id
            )

    def get_drift_summary(self, repository_id: RepositoryId) -> Dict[str, Any]:
        """Get an aggregated summary of drift categories and security crossings."""
        with self._uow_factory() as uow:
            return uow.behavior_drift.get_drift_summary(repository_id)
