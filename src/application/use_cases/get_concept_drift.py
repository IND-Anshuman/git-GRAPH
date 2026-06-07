"""Use case for calculating concept drift between two historical commits."""

import uuid
from typing import Callable
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.services.concept_drift_engine import ConceptDriftEngine


class GetConceptDriftUseCase:
    """Calculates multidimensional drift between two versions of a concept."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork], drift_engine: ConceptDriftEngine) -> None:
        self.uow_factory = uow_factory
        self.drift_engine = drift_engine

    def execute(self, concept_id: uuid.UUID, baseline_commit: str, current_commit: str) -> dict:
        """
        Computes drift metrics comparing baseline and current commits.

        Args:
            concept_id: The UUID of the ConceptNode.
            baseline_commit: The baseline commit hash.
            current_commit: The current commit hash.

        Returns:
            A dictionary containing drift scores and categories.
        """
        with self.uow_factory() as uow:
            existing_drift = uow.concept_drift.get_by_concept_and_commits(concept_id, baseline_commit, current_commit)
            if existing_drift:
                return {
                    "concept_id": str(concept_id),
                    "drift_score": float(existing_drift.drift_score),
                    "drift_category": existing_drift.drift_category,
                    "dimension_scores": existing_drift.dimension_scores,
                }

            base_ver = uow.concept_versions.get_by_concept_at_commit(concept_id, baseline_commit)
            curr_ver = uow.concept_versions.get_by_concept_at_commit(concept_id, current_commit)

            if not base_ver or not curr_ver:
                raise ValueError("Concept versions not found at baseline or current commit.")

            drift = self.drift_engine.compute_drift(uow, concept_id, base_ver, curr_ver)

            return {
                "concept_id": str(concept_id),
                "drift_score": float(drift.drift_score),
                "drift_category": drift.drift_category,
                "dimension_scores": drift.dimension_scores,
            }
