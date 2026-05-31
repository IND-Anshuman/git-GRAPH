import uuid
from typing import Callable
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.dtos.responses import RelationshipResponse
from src.domain.enums import RelationshipType

class QueryRelationshipsUseCase:
    def __init__(self, uow_factory: Callable[[], IUnitOfWork]):
        self.uow_factory = uow_factory

    def execute(
        self, 
        repository_id: str, 
        relationship_type: str | None = None, 
        offset: int = 0, 
        limit: int = 50
    ) -> tuple[list[RelationshipResponse], int]:
        repo_uuid = uuid.UUID(repository_id)
        parsed_type = RelationshipType(relationship_type) if relationship_type else None
        
        with self.uow_factory() as uow:
            relationships = uow.relationships.get_by_repository(repo_uuid)
            
            if parsed_type:
                relationships = [r for r in relationships if r.relationship_type == parsed_type]
            
            total = len(relationships)
            paginated = relationships[offset:offset + limit]
            
            responses = []
            for r in paginated:
                source_entity = uow.code_entities.get_by_seid(r.source_seid)
                target_entity = uow.code_entities.get_by_seid(r.target_seid)
                
                responses.append(RelationshipResponse(
                    id=str(r.id),
                    relationship_type=r.relationship_type.value,
                    source_seid=str(r.source_seid.value),
                    target_seid=str(r.target_seid.value),
                    source_name=source_entity.name if source_entity else None,
                    target_name=target_entity.name if target_entity else None,
                    confidence=r.confidence,
                    metadata=r.metadata
                ))
                
            return responses, total
