"""FastAPI API routes for temporal graph queries and walking controls."""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List

from src.presentation.schemas.responses import (
    CommitSchema,
    EntityVersionSchema,
    ChangeEventSchema,
    TemporalGraphSchema,
    TimelineSchema
)
from src.application.use_cases.scan_repository_history import ScanRepositoryHistoryUseCase
from src.application.use_cases.get_commits import GetCommitsUseCase
from src.application.use_cases.get_entity_history import GetEntityHistoryUseCase
from src.application.use_cases.get_commit_changes import GetCommitChangesUseCase
from src.application.use_cases.get_repository_timeline import GetRepositoryTimelineUseCase
from src.application.use_cases.reconstruct_graph import ReconstructGraphUseCase

from src.presentation.dependencies import (
    get_scan_history_use_case,
    get_get_commits_use_case,
    get_entity_history_use_case,
    get_commit_changes_use_case,
    get_repository_timeline_use_case,
    get_reconstruct_graph_use_case,
    get_uow_factory
)

temporal_router = APIRouter(tags=["temporal"])

@temporal_router.post("/repositories/{repository_id}/scan-history", status_code=status.HTTP_202_ACCEPTED)
def scan_repository_history(
    repository_id: str,
    background_tasks: BackgroundTasks,
    branch: str = "main",
    use_case: ScanRepositoryHistoryUseCase = Depends(get_scan_history_use_case)
):
    """Triggers a background history scan and temporal diff generation for the repository."""
    background_tasks.add_task(use_case.execute, repository_id, branch)
    return {"status": "scanning", "message": "History scan has been queued in the background."}

@temporal_router.get("/repositories/{repository_id}/timeline", response_model=List[TimelineSchema])
def get_repository_timeline(
    repository_id: str,
    use_case: GetRepositoryTimelineUseCase = Depends(get_repository_timeline_use_case)
):
    """Retrieves the chronological timeline of commit events and entity changes."""
    return use_case.execute(repository_id)

@temporal_router.get("/repositories/{repository_id}/commits", response_model=List[CommitSchema])
def get_commits(
    repository_id: str,
    use_case: GetCommitsUseCase = Depends(get_get_commits_use_case)
):
    """Retrieves all analyzed commits for the repository."""
    return use_case.execute(repository_id)

@temporal_router.get("/entities/{entity_id}/history", response_model=List[EntityVersionSchema])
def get_entity_history(
    entity_id: str,
    use_case: GetEntityHistoryUseCase = Depends(get_entity_history_use_case)
):
    """Retrieves the chronological version history of a specific entity by its SEID."""
    return use_case.execute(entity_id)

@temporal_router.get("/commits/{commit_hash}", response_model=CommitSchema)
def get_commit(
    commit_hash: str,
    uow_factory = Depends(get_uow_factory)
):
    """Retrieves details for a single analyzed commit."""
    with uow_factory() as uow:
        commit = uow.commits.get_by_hash(commit_hash)
        if not commit:
            raise HTTPException(status_code=404, detail=f"Commit {commit_hash} not found.")
        return CommitSchema(
            hash=commit.hash,
            repository_id=str(commit.repository_id),
            author=commit.author,
            email=commit.email,
            timestamp=commit.timestamp,
            message=commit.message,
            parent_hashes=commit.parent_hashes,
            is_merge=commit.is_merge,
            is_root=commit.is_root
        )

@temporal_router.get("/commits/{commit_hash}/changes", response_model=List[ChangeEventSchema])
def get_commit_changes(
    commit_hash: str,
    use_case: GetCommitChangesUseCase = Depends(get_commit_changes_use_case)
):
    """Retrieves all entity change events introduced by the commit."""
    return use_case.execute(commit_hash)

@temporal_router.get("/commits/{commit_hash}/graph", response_model=TemporalGraphSchema)
def get_commit_graph(
    commit_hash: str,
    repository_id: str,
    use_case: ReconstructGraphUseCase = Depends(get_reconstruct_graph_use_case)
):
    """Reconstructs the active entities and relationships graph as-of this commit."""
    try:
        return use_case.execute(repository_id, commit_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
