"""Use case for fetching the behavioral drift metrics of a transition."""

from typing import Callable, Optional
import uuid

from src.application.dtos.logic_responses import (
    BehaviorDriftResponse,
    DriftDimensionsResponse,
)
from src.application.ports.unit_of_work import IUnitOfWork


class GetBehaviorDriftUseCase:
    """Retrieves the BehaviorDrift measurements associated with a transition."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(self, transition_id_str: str) -> Optional[BehaviorDriftResponse]:
        """Fetch the behavior drift details associated with the given LogicTransition UUID."""
        trans_id = uuid.UUID(transition_id_str)
        with self.uow_factory() as uow:
            drift = uow.behavior_drift.get_by_transition(trans_id)
            if not drift:
                return None

            dims = DriftDimensionsResponse(
                structural_drift=drift.dimension_scores.structural_drift,
                dependency_drift=drift.dimension_scores.dependency_drift,
                api_surface_drift=drift.dimension_scores.api_surface_drift,
                control_flow_drift=drift.dimension_scores.control_flow_drift,
                ontology_drift=drift.dimension_scores.ontology_drift,
                security_drift=drift.dimension_scores.security_drift,
            )

            return BehaviorDriftResponse(
                id=str(drift.id),
                logic_transition_id=str(drift.logic_transition_id),
                from_logic_version_id=str(drift.from_logic_version_id),
                to_logic_version_id=str(drift.to_logic_version_id),
                drift_score=drift.drift_score,
                drift_category=drift.drift_category.value,
                dimension_scores=dims,
                ontology_changed=drift.ontology_changed,
                security_boundary_crossed=drift.security_boundary_crossed,
                computed_at=drift.computed_at,
                metadata=drift.metadata,
            )
