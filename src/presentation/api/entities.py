from fastapi import APIRouter, Depends
from src.presentation.schemas.responses import EntitySchema, PaginatedResponse
from src.presentation.schemas.pagination import PaginationParams
from src.application.use_cases.query_entities import QueryEntitiesUseCase
from src.presentation.dependencies import get_query_entities_use_case

entity_router = APIRouter(prefix="/repositories", tags=["entities"])

@entity_router.get("/{repository_id}/entities", response_model=PaginatedResponse[EntitySchema])
def query_entities(
    repository_id: str,
    entity_type: str | None = None,
    pagination: PaginationParams = Depends(),
    use_case: QueryEntitiesUseCase = Depends(get_query_entities_use_case)
):
    responses, total = use_case.execute(
        repository_id=repository_id,
        entity_type=entity_type,
        offset=pagination.offset,
        limit=pagination.limit
    )
    return PaginatedResponse(
        items=responses,
        total=total,
        offset=pagination.offset,
        limit=pagination.limit
    )
