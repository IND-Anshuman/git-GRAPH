from fastapi import Request
from typing import Callable, Any
from src.application.use_cases.ingest_repository import IngestRepositoryUseCase
from src.application.use_cases.get_repository import GetRepositoryUseCase
from src.application.use_cases.query_entities import QueryEntitiesUseCase
from src.application.use_cases.query_relationships import QueryRelationshipsUseCase

def get_container(request: Request) -> Any:
    return request.app.state.container

def get_uow_factory(request: Request) -> Callable:
    return request.app.state.container.get_uow_factory()

def get_ingest_use_case(request: Request) -> IngestRepositoryUseCase:
    return request.app.state.container.get_ingest_repository_use_case()

def get_get_repository_use_case(request: Request) -> GetRepositoryUseCase:
    return request.app.state.container.get_get_repository_use_case()

def get_query_entities_use_case(request: Request) -> QueryEntitiesUseCase:
    return request.app.state.container.get_query_entities_use_case()

def get_query_relationships_use_case(request: Request) -> QueryRelationshipsUseCase:
    return request.app.state.container.get_query_relationships_use_case()
