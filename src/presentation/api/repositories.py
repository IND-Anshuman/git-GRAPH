from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Any
from src.presentation.schemas.requests import CreateRepositoryRequest
from src.presentation.schemas.responses import RepositorySchema, IngestionResultSchema, PaginatedResponse
from src.application.dtos.commands import IngestRepositoryCommand
from src.application.use_cases.ingest_repository import IngestRepositoryUseCase
from src.application.use_cases.get_repository import GetRepositoryUseCase
from src.domain.exceptions import RepositoryNotFoundException
from src.presentation.dependencies import get_ingest_use_case, get_get_repository_use_case, get_uow_factory

repository_router = APIRouter(prefix="/repositories", tags=["repositories"])

@repository_router.post("", response_model=IngestionResultSchema, status_code=status.HTTP_202_ACCEPTED)
def ingest_repository(
    request: CreateRepositoryRequest,
    use_case: IngestRepositoryUseCase = Depends(get_ingest_use_case)
):
    command = IngestRepositoryCommand(
        url=str(request.url),
        branch=request.branch,
        name=request.name
    )
    result = use_case.execute(command)
    return result

@repository_router.get("/{repository_id}", response_model=RepositorySchema)
def get_repository(
    repository_id: str,
    use_case: GetRepositoryUseCase = Depends(get_get_repository_use_case)
):
    try:
        result = use_case.execute(repository_id)
        return result
    except RepositoryNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@repository_router.get("", response_model=list[RepositorySchema])
def list_repositories(uow_factory: Any = Depends(get_uow_factory)):
    with uow_factory() as uow:
        repos = uow.repositories.list_all()
        return [
            RepositorySchema(
                id=str(r.id),
                name=r.name,
                url=r.url,
                default_branch=r.default_branch,
                status=r.status.value,
                entity_count=r.metadata.get("entities_count"),
                file_count=r.metadata.get("files_count"),
                created_at=r.created_at,
                updated_at=r.updated_at
            ) for r in repos
        ]
