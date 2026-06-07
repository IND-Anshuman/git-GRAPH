"""Use case for retrieving deterministic concept explanation breakdown details."""

import uuid
from typing import Callable
from src.application.ports.unit_of_work import IUnitOfWork


class GetConceptExplanationUseCase:
    """Retrieves deterministic explanation detail statistics for a concept version."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(self, concept_version_id: uuid.UUID) -> dict:
        """
        Retrieves explanation statistics for a concept version.

        Args:
            concept_version_id: The UUID of the ConceptVersion.

        Returns:
            A dictionary of explanation summary and details.
        """
        with self.uow_factory() as uow:
            explanation = uow.concept_explanations.get_by_concept_version(concept_version_id)
            if not explanation:
                raise ValueError(f"Concept explanation not found for version {concept_version_id}.")

            return {
                "id": str(explanation.id),
                "concept_version_id": str(explanation.concept_version_id),
                "summary": explanation.summary,
                "detail": explanation.detail,
            }
