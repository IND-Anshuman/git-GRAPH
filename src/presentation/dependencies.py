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

# Phase 3 Use Cases
from src.application.use_cases.extract_logic_use_case import ExtractLogicUseCase
from src.application.use_cases.get_entity_logic_use_case import GetEntityLogicUseCase
from src.application.use_cases.get_entity_logic_history_use_case import GetEntityLogicHistoryUseCase
from src.application.use_cases.get_behavior_evolution_use_case import GetBehaviorEvolutionUseCase
from src.application.use_cases.get_logic_evidence_use_case import GetLogicEvidenceUseCase
from src.application.use_cases.get_behavior_explanation_use_case import GetBehaviorExplanationUseCase
from src.application.use_cases.get_behavior_drift_use_case import GetBehaviorDriftUseCase
from src.application.use_cases.validate_logic_use_case import ValidateLogicUseCase


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

def get_health_score_engine(request: Request) -> Any:
    return request.app.state.container.health_score_engine

def get_temporal_integrity_service(request: Request) -> Any:
    return request.app.state.container.temporal_integrity_service

def get_temporal_explorer(request: Request) -> Any:
    return request.app.state.container.temporal_explorer

def get_temporal_replay_service(request: Request) -> Any:
    return request.app.state.container.temporal_replay_service

def get_extract_logic_use_case(request: Request) -> ExtractLogicUseCase:
    return request.app.state.container.get_extract_logic_use_case()

def get_get_entity_logic_use_case(request: Request) -> GetEntityLogicUseCase:
    return request.app.state.container.get_get_entity_logic_use_case()

def get_get_entity_logic_history_use_case(request: Request) -> GetEntityLogicHistoryUseCase:
    return request.app.state.container.get_get_entity_logic_history_use_case()

def get_get_behavior_evolution_use_case(request: Request) -> GetBehaviorEvolutionUseCase:
    return request.app.state.container.get_get_behavior_evolution_use_case()

def get_get_logic_evidence_use_case(request: Request) -> GetLogicEvidenceUseCase:
    return request.app.state.container.get_get_logic_evidence_use_case()

def get_get_behavior_explanation_use_case(request: Request) -> GetBehaviorExplanationUseCase:
    return request.app.state.container.get_get_behavior_explanation_use_case()

def get_get_behavior_drift_use_case(request: Request) -> GetBehaviorDriftUseCase:
    return request.app.state.container.get_get_behavior_drift_use_case()

def get_validate_logic_use_case(request: Request) -> ValidateLogicUseCase:
    return request.app.state.container.get_validate_logic_use_case()
