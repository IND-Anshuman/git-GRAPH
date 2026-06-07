"""Use case for retrieving the historical evolution timeline of a concept."""

import uuid
from typing import Callable, List
from src.application.ports.unit_of_work import IUnitOfWork


class GetConceptEvolutionUseCase:
    """Retrieves chronological snapshots and transitions for a concept node."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(self, concept_id: uuid.UUID) -> List[dict]:
        """
        Retrieves the evolution history of a concept.

        Args:
            concept_id: The UUID of the ConceptNode.

        Returns:
            A list of chronological concept versions with transitions.
        """
        with self.uow_factory() as uow:
            # Fetch all versions sorted chronologically
            versions = uow.concept_versions.list_by_concept(concept_id)
            versions.sort(key=lambda v: v.version_number)

            results = []
            for ver in versions:
                transition_data = None
                evos = uow.concept_evolution.list_by_to_version(ver.id)
                if evos:
                    evo = evos[0]
                    transition_data = {
                        "type": evo.transition_type.value if hasattr(evo.transition_type, "value") else str(evo.transition_type),
                        "similarity_score": float(evo.similarity_score),
                    }
                else:
                    transition_data = {
                        "type": "CONCEPT_CREATION",
                        "similarity_score": 1.0,
                    }

                results.append(
                    {
                        "concept_version_id": str(ver.id),
                        "commit_hash": ver.commit_hash,
                        "version_number": ver.version_number,
                        "confidence": float(ver.confidence),
                        "transition": transition_data,
                    }
                )

            return results
