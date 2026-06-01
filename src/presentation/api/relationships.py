from fastapi import APIRouter, Depends
from src.presentation.schemas.responses import RelationshipSchema, PaginatedResponse
from src.presentation.schemas.pagination import PaginationParams
from src.application.use_cases.query_relationships import QueryRelationshipsUseCase
from src.presentation.dependencies import get_query_relationships_use_case

relationship_router = APIRouter(prefix="/repositories", tags=["relationships"])

@relationship_router.get("/{repository_id}/relationships", response_model=PaginatedResponse[RelationshipSchema])
def query_relationships(
    repository_id: str,
    relationship_type: str | None = None,
    pagination: PaginationParams = Depends(),
    use_case: QueryRelationshipsUseCase = Depends(get_query_relationships_use_case)
):
    responses, total = use_case.execute(
        repository_id=repository_id,
        relationship_type=relationship_type,
        offset=pagination.offset,
        limit=pagination.limit
    )
    return PaginatedResponse(
        items=responses,
        total=total,
        offset=pagination.offset,
        limit=pagination.limit
    )
