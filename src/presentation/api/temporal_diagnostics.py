"""FastAPI API routes for temporal diagnostics, integrity checks, repairs, and metrics."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.value_objects.repository_id import RepositoryId
from src.presentation.schemas.requests import ExecuteRepairRequest
from src.presentation.schemas.responses import (
    HealthScoreSchema,
    IntegrityViolationSchema,
    RepairAuditSchema,
    BenchmarkReportSchema
)
from src.presentation.dependencies import (
    get_health_score_engine,
    get_temporal_integrity_service,
    get_uow_factory
)

diagnostics_router = APIRouter(tags=["diagnostics"])

@diagnostics_router.get(
    "/repositories/{repository_id}/diagnostics/health",
    response_model=HealthScoreSchema
)
def get_repository_health(
    repository_id: str,
    uow_factory = Depends(get_uow_factory),
    health_engine = Depends(get_health_score_engine)
):
    """Calculates and returns the system-wide health score metrics for the repository."""
    try:
        repo_uuid = uuid.UUID(repository_id)
        repo_id = RepositoryId(repo_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository UUID format.")

    with uow_factory() as uow:
        # Check if repository exists
        repo = uow.repositories.get_by_id(repo_id)
        if not repo:
            raise HTTPException(
                status_code=404,
                detail=f"Repository {repository_id} not found."
            )
        
        # Calculate health score
        try:
            health_report = health_engine.calculate_health_score(uow, repo_id)
            return health_report
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating health score: {str(e)}"
            )

@diagnostics_router.get(
    "/repositories/{repository_id}/diagnostics/integrity",
    response_model=List[IntegrityViolationSchema]
)
def get_repository_integrity(
    repository_id: str,
    unresolved_only: bool = True,
    uow_factory = Depends(get_uow_factory),
    integrity_service = Depends(get_temporal_integrity_service)
):
    """Runs structural consistency checks and returns active/unresolved violations."""
    try:
        repo_uuid = uuid.UUID(repository_id)
        repo_id = RepositoryId(repo_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository UUID format.")

    with uow_factory() as uow:
        repo = uow.repositories.get_by_id(repo_id)
        if not repo:
            raise HTTPException(
                status_code=404,
                detail=f"Repository {repository_id} not found."
            )

        try:
            violations = integrity_service.perform_integrity_check(uow, repo_id)
            uow.commit() # Save the violations
            
            # Map violations to response schema list
            result = []
            for v in violations:
                if unresolved_only and v.is_resolved:
                    continue
                result.append(
                    IntegrityViolationSchema(
                        id=str(v.id),
                        repository_id=str(v.repository_id.value if isinstance(v.repository_id, RepositoryId) else v.repository_id),
                        violation_type=v.violation_type,
                        severity=v.severity,
                        target_seid=v.target_seid,
                        description=v.description,
                        recommended_repair=v.recommended_repair,
                        is_resolved=v.is_resolved,
                        detected_at=v.detected_at
                    )
                )
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error performing integrity check: {str(e)}"
            )

@diagnostics_router.post(
    "/repositories/{repository_id}/diagnostics/repair",
    response_model=RepairAuditSchema
)
def execute_repository_repair(
    repository_id: str,
    request: ExecuteRepairRequest,
    uow_factory = Depends(get_uow_factory),
    integrity_service = Depends(get_temporal_integrity_service)
):
    """Executes transactional repair operations on specified structural violations."""
    try:
        repo_uuid = uuid.UUID(repository_id)
        repo_id = RepositoryId(repo_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository UUID format.")

    try:
        violation_uuids = [uuid.UUID(vid) for vid in request.issue_ids]
    except ValueError:
        raise HTTPException(status_code=400, detail="One or more invalid violation UUID formats.")

    with uow_factory() as uow:
        repo = uow.repositories.get_by_id(repo_id)
        if not repo:
            raise HTTPException(
                status_code=404,
                detail=f"Repository {repository_id} not found."
            )

        try:
            audit = integrity_service.execute_repairs(
                uow, repo_id, violation_uuids, operator=request.operator
            )
            uow.commit()
            
            return RepairAuditSchema(
                id=str(audit.id),
                repository_id=str(audit.repository_id.value if isinstance(audit.repository_id, RepositoryId) else audit.repository_id),
                operator=audit.operator,
                issue_ids=[str(i) for i in audit.issue_ids],
                repair_actions=audit.repair_actions,
                executed_at=audit.executed_at
            )
        except Exception as e:
            uow.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error executing repairs: {str(e)}"
            )

@diagnostics_router.get(
    "/repositories/{repository_id}/diagnostics/benchmarks",
    response_model=List[BenchmarkReportSchema]
)
def get_repository_benchmarks(
    repository_id: str,
    uow_factory = Depends(get_uow_factory)
):
    """Retrieves all performance benchmark scan logs for a repository."""
    try:
        repo_uuid = uuid.UUID(repository_id)
        repo_id = RepositoryId(repo_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository UUID format.")

    with uow_factory() as uow:
        repo = uow.repositories.get_by_id(repo_id)
        if not repo:
            raise HTTPException(
                status_code=404,
                detail=f"Repository {repository_id} not found."
            )

        try:
            reports = uow.metrics.list_benchmark_reports(repo_id)
            return [
                BenchmarkReportSchema(
                    id=str(r.id),
                    repository_id=str(r.repository_id.value if isinstance(r.repository_id, RepositoryId) else r.repository_id),
                    commit_hash=r.commit_hash,
                    scan_duration_ms=r.scan_duration_ms,
                    diff_throughput_nodes_sec=r.diff_throughput_nodes_sec,
                    reconstruction_latency_ms=r.reconstruction_latency_ms,
                    db_size_bytes=r.db_size_bytes,
                    memory_rss_bytes=r.memory_rss_bytes,
                    measured_at=r.measured_at
                )
                for r in reports
            ]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving benchmark reports: {str(e)}"
            )
