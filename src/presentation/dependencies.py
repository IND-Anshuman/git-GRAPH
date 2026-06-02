from fastapi import Request
from typing import Callable, Any
from src.application.use_cases.ingest_repository import IngestRepositoryUseCase
from src.application.use_cases.get_repository import GetRepositoryUseCase
from src.application.use_cases.query_entities import QueryEntitiesUseCase
from src.application.use_cases.query_relationships import QueryRelationshipsUseCase
from src.application.use_cases.scan_repository_history import ScanRepositoryHistoryUseCase
from src.application.use_cases.get_commits import GetCommitsUseCase
from src.application.use_cases.get_entity_history import GetEntityHistoryUseCase
from src.application.use_cases.get_commit_changes import GetCommitChangesUseCase
from src.application.use_cases.get_repository_timeline import GetRepositoryTimelineUseCase
from src.application.use_cases.reconstruct_graph import ReconstructGraphUseCase

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

def get_scan_history_use_case(request: Request) -> ScanRepositoryHistoryUseCase:
    return request.app.state.container.get_scan_repository_history_use_case()

def get_get_commits_use_case(request: Request) -> GetCommitsUseCase:
    return request.app.state.container.get_get_commits_use_case()

def get_entity_history_use_case(request: Request) -> GetEntityHistoryUseCase:
    return request.app.state.container.get_entity_history_use_case()

def get_commit_changes_use_case(request: Request) -> GetCommitChangesUseCase:
    return request.app.state.container.get_commit_changes_use_case()

def get_repository_timeline_use_case(request: Request) -> GetRepositoryTimelineUseCase:
    return request.app.state.container.get_repository_timeline_use_case()

def get_reconstruct_graph_use_case(request: Request) -> ReconstructGraphUseCase:
    return request.app.state.container.get_reconstruct_graph_use_case()
