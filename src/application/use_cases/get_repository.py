import uuid
from typing import Callable, Any
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.dtos.responses import RepositoryResponse
from src.domain.exceptions import RepositoryNotFoundException

class GetRepositoryUseCase:
    def __init__(self, uow_factory: Callable[[], IUnitOfWork]):
        self.uow_factory = uow_factory

    def execute(self, repository_id: str) -> RepositoryResponse:
        try:
            repo_uuid = uuid.UUID(repository_id)
        except ValueError:
            raise RepositoryNotFoundException(f"Invalid repository ID format: {repository_id}")

        with self.uow_factory() as uow:
            repo = uow.repositories.get_by_id(repo_uuid)
            if not repo:
                raise RepositoryNotFoundException(f"Repository {repository_id} not found")
                
            return RepositoryResponse(
                id=str(repo.id),
                name=repo.name,
                url=repo.url,
                default_branch=repo.default_branch,
                status=repo.status.name,
                entity_count=repo.metadata.get("entities_count"),
                file_count=repo.metadata.get("files_count"),
                created_at=repo.created_at,
                updated_at=repo.updated_at
            )
