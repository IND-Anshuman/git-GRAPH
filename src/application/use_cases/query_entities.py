import uuid
from typing import Callable
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.dtos.responses import EntityResponse
from src.domain.enums import EntityType

class QueryEntitiesUseCase:
    def __init__(self, uow_factory: Callable[[], IUnitOfWork]):
        self.uow_factory = uow_factory

    def execute(
        self, 
        repository_id: str, 
        entity_type: str | None = None, 
        offset: int = 0, 
        limit: int = 50
    ) -> tuple[list[EntityResponse], int]:
        repo_uuid = uuid.UUID(repository_id)
        parsed_type = EntityType(entity_type) if entity_type else None
        
        with self.uow_factory() as uow:
            entities = uow.code_entities.get_by_repository(repo_uuid)
            
            if parsed_type:
                entities = [e for e in entities if e.entity_type == parsed_type]
            
            total = len(entities)
            paginated = entities[offset:offset + limit]
            
            responses = []
            for e in paginated:
                source_file = uow.source_files.get_by_id(e.file_id)
                file_path = source_file.file_path if source_file else "unknown"
                
                responses.append(EntityResponse(
                    seid=str(e.seid.value),
                    entity_type=e.entity_type.value,
                    name=e.name,
                    qualified_name=str(e.qualified_name),
                    file_path=file_path,
                    language=e.language.value,
                    start_line=e.location.start_point.line,
                    end_line=e.location.end_point.line,
                    parent_seid=str(e.parent_seid.value) if e.parent_seid else None,
                    metadata=e.metadata
                ))
                
            return responses, total
