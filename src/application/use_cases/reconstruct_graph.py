"""Use case for reconstructing the graph at a specific commit hash."""

from typing import Callable, Optional
import uuid

from src.application.ports.unit_of_work import IUnitOfWork
from src.application.services.historical_reconstruction import HistoricalReconstructionService
from src.application.dtos.responses import TemporalGraphResponse, EntityResponse, RelationshipResponse
from src.domain.value_objects.repository_id import RepositoryId

class ReconstructGraphUseCase:
    """Reconstructs the graph of active entities and relationships at a specific commit."""

    def __init__(
        self,
        reconstruction_service: HistoricalReconstructionService,
        uow_factory: Callable[[], IUnitOfWork]
    ) -> None:
        self.reconstruction_service = reconstruction_service
        self.uow_factory = uow_factory

    def execute(self, repository_id: str, commit_hash: str) -> TemporalGraphResponse:
        """Execute historical reconstruction for a repository and commit."""
        repo_id = RepositoryId(uuid.UUID(repository_id))
        with self.uow_factory() as uow:
            entities, relationships = self.reconstruction_service.reconstruct_graph_at_commit(
                uow, repo_id, commit_hash
            )
            
            entities_dto = [
                EntityResponse(
                    seid=str(e.seid),
                    entity_type=e.entity_type.name,
                    name=e.name,
                    qualified_name=e.qualified_name,
                    file_path=e.location.file_path,
                    language=e.language.name,
                    start_line=e.location.start_line,
                    end_line=e.location.end_line,
                    parent_seid=str(e.parent_seid) if e.parent_seid else None,
                    metadata=e.metadata
                )
                for e in entities
            ]
            
            relationships_dto = [
                RelationshipResponse(
                    id=str(r.id),
                    relationship_type=r.relationship_type.name,
                    source_seid=str(r.source_seid),
                    target_seid=str(r.target_seid),
                    source_name=None, # we don't resolve names eagerly here
                    target_name=None,
                    confidence=r.confidence,
                    metadata=r.metadata
                )
                for r in relationships
            ]
            
            return TemporalGraphResponse(
                entities=entities_dto,
                relationships=relationships_dto
            )
