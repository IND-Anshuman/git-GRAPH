"""REST API endpoints for Phase 4 Concept Graph and Intelligence."""

from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases.detect_concepts import DetectConceptsUseCase
from src.application.use_cases.get_concepts import GetConceptsUseCase
from src.application.use_cases.get_concept_evolution import GetConceptEvolutionUseCase
from src.application.use_cases.get_concept_relationships import GetConceptRelationshipsUseCase
from src.application.use_cases.get_concept_drift import GetConceptDriftUseCase
from src.application.use_cases.get_concept_explanation import GetConceptExplanationUseCase
from src.application.services.concept_backfill_service import ConceptBackfillService
from src.presentation.schemas.concept_schemas import (
    ConceptResponse,
    ConceptEvolutionResponse,
    ConceptDriftResponse,
    ConceptMapResponse,
    ConceptExplanationResponse,
    BackfillResponse,
)
from src.presentation.dependencies import (
    get_detect_concepts_use_case,
    get_get_concepts_use_case,
    get_get_concept_evolution_use_case,
    get_get_concept_relationships_use_case,
    get_get_concept_drift_use_case,
    get_get_concept_explanation_use_case,
    get_concept_backfill_service,
)

concepts_router = APIRouter(tags=["concepts"])


@concepts_router.post("/repositories/{id}/concepts/extract", status_code=status.HTTP_202_ACCEPTED)
def extract_concepts(
    id: str,
    commit_hash: str,
    use_case: DetectConceptsUseCase = Depends(get_detect_concepts_use_case),
):
    """Trigger concept extraction for a specific repository and commit hash."""
    try:
        repo_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository UUID format.")

    try:
        summary = use_case.execute(repo_uuid, commit_hash)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@concepts_router.get("/repositories/{id}/concepts", response_model=List[ConceptResponse])
def get_concepts(
    id: str,
    commit: Optional[str] = None,
    domain: Optional[str] = None,
    use_case: GetConceptsUseCase = Depends(get_get_concepts_use_case),
):
    """Retrieve list of concepts detected in a repository at a commit, optionally filtered by domain."""
    try:
        repo_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository UUID format.")

    try:
        return use_case.execute(repo_uuid, commit, domain)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@concepts_router.get("/concepts/{id}/timeline", response_model=List[ConceptEvolutionResponse])
def get_concept_timeline(
    id: str,
    use_case: GetConceptEvolutionUseCase = Depends(get_get_concept_evolution_use_case),
):
    """Retrieve the chronological evolution history/timeline of a concept node."""
    try:
        concept_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid concept UUID format.")

    return use_case.execute(concept_uuid)


@concepts_router.get("/concepts/{id}/drift", response_model=ConceptDriftResponse)
def get_concept_drift(
    id: str,
    baseline_commit: str,
    current_commit: str,
    use_case: GetConceptDriftUseCase = Depends(get_get_concept_drift_use_case),
):
    """Retrieve multi-dimensional conceptual drift scores between two commits."""
    try:
        concept_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid concept UUID format.")

    try:
        return use_case.execute(concept_uuid, baseline_commit, current_commit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@concepts_router.get("/repositories/{id}/concept-map", response_model=ConceptMapResponse)
def get_concept_map(
    id: str,
    commit: Optional[str] = None,
    use_case: GetConceptRelationshipsUseCase = Depends(get_get_concept_relationships_use_case),
):
    """Retrieve nodes and edges representing the dependency graph of concepts at a commit."""
    try:
        repo_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository UUID format.")

    try:
        return use_case.execute(repo_uuid, commit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@concepts_router.get("/concepts/version/{version_id}/explanation", response_model=ConceptExplanationResponse)
def get_concept_explanation(
    version_id: str,
    use_case: GetConceptExplanationUseCase = Depends(get_get_concept_explanation_use_case),
):
    """Retrieve the structured deterministic explanation summary and details for a concept version."""
    try:
        ver_uuid = uuid.UUID(version_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid concept version UUID format.")

    try:
        return use_case.execute(ver_uuid)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@concepts_router.post("/repositories/{id}/concepts/backfill", response_model=BackfillResponse)
def backfill_concepts(
    id: str,
    service: ConceptBackfillService = Depends(get_concept_backfill_service),
):
    """Manually trigger historical concept extraction and backfill over all commits in the database."""
    try:
        repo_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository UUID format.")

    try:
        summary = service.backfill_repository(repo_uuid)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
