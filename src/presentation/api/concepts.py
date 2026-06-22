"""REST API endpoints for Phase 4 Concept Graph and Intelligence."""

from typing import Callable, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks

from src.application.use_cases.detect_concepts import DetectConceptsUseCase
from src.application.use_cases.extract_all_in_one_concepts_use_case import ExtractAllInOneConceptsUseCase
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
    FrameworkDefinitionResponse,
    FrameworkVersionResponse,
    BehaviorFamilyResponse,
    CanonicalBehaviorResponse,
    BehaviorAliasResponse,
    CanonicalFlowResponse,
)
from src.presentation.dependencies import (
    get_detect_concepts_use_case,
    get_get_concepts_use_case,
    get_get_concept_evolution_use_case,
    get_get_concept_relationships_use_case,
    get_get_concept_drift_use_case,
    get_get_concept_explanation_use_case,
    get_concept_backfill_service,
    get_extract_all_in_one_concepts_use_case,
    get_uow_factory,
)
from src.infrastructure.persistence.models.concept_models import (
    FrameworkDefinitionModel,
    FrameworkVersionModel,
    BehaviorFamilyModel,
    CanonicalBehaviorModel,
    BehaviorAliasModel,
    CanonicalFlowModel,
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


@concepts_router.post("/repositories/{id}/concepts/extract-all-in-one", status_code=status.HTTP_202_ACCEPTED)
def extract_all_in_one_concepts(
    id: str,
    background_tasks: BackgroundTasks,
    commit_hash: Optional[str] = None,
    use_case: ExtractAllInOneConceptsUseCase = Depends(get_extract_all_in_one_concepts_use_case),
):
    """Trigger all-in-one logic and concept extraction. Runs asynchronously if repository-wide."""
    try:
        uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository UUID format.")

    if commit_hash:
        try:
            return use_case.execute(id, commit_hash)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        background_tasks.add_task(use_case.execute, id)
        return {"status": "success", "message": "All-in-one logic and concept extraction started asynchronously."}


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


@concepts_router.get("/frameworks/definitions", response_model=List[FrameworkDefinitionResponse])
def get_framework_definitions(
    uow_factory: Callable = Depends(get_uow_factory),
):
    """Retrieve all framework definitions registered in the system."""
    with uow_factory() as uow:
        defs = uow._session.query(FrameworkDefinitionModel).all()
        return [
            FrameworkDefinitionResponse(
                id=d.id,
                framework_name=d.framework_name,
                language=d.language,
                metadata=d.metadata_
            )
            for d in defs
        ]


@concepts_router.get("/frameworks/versions", response_model=List[FrameworkVersionResponse])
def get_framework_versions(
    uow_factory: Callable = Depends(get_uow_factory),
):
    """Retrieve all framework versions from the registry."""
    with uow_factory() as uow:
        versions = uow._session.query(FrameworkVersionModel).all()
        return [
            FrameworkVersionResponse(
                id=str(v.id),
                framework_id=v.framework_id,
                version_string=v.version_string,
                supported_syntax_rules=v.supported_syntax_rules,
                released_at=v.released_at
            )
            for v in versions
        ]


@concepts_router.get("/behaviors/families", response_model=List[BehaviorFamilyResponse])
def get_behavior_families(
    uow_factory: Callable = Depends(get_uow_factory),
):
    """Retrieve all registered behavior families."""
    with uow_factory() as uow:
        families = uow._session.query(BehaviorFamilyModel).all()
        return [
            BehaviorFamilyResponse(
                id=f.id,
                name=f.name,
                parent_concept_id=f.parent_concept_id,
                description=f.description
            )
            for f in families
        ]


@concepts_router.get("/behaviors/canonical", response_model=List[CanonicalBehaviorResponse])
def get_canonical_behaviors(
    uow_factory: Callable = Depends(get_uow_factory),
):
    """Retrieve all canonical behaviors."""
    with uow_factory() as uow:
        behaviors = uow._session.query(CanonicalBehaviorModel).all()
        return [
            CanonicalBehaviorResponse(
                id=b.id,
                name=b.name,
                family_id=b.family_id,
                description=b.description,
                created_at=b.created_at
            )
            for b in behaviors
        ]


@concepts_router.get("/behaviors/aliases", response_model=List[BehaviorAliasResponse])
def get_behavior_aliases(
    uow_factory: Callable = Depends(get_uow_factory),
):
    """Retrieve all language-specific behavior pattern aliases."""
    with uow_factory() as uow:
        aliases = uow._session.query(BehaviorAliasModel).all()
        return [
            BehaviorAliasResponse(
                id=str(a.id),
                canonical_behavior_id=a.canonical_behavior_id,
                language=a.language,
                imports=a.imports,
                calls=a.calls,
                heuristics=a.heuristics
            )
            for a in aliases
        ]


@concepts_router.get("/flows", response_model=List[CanonicalFlowResponse])
def get_canonical_flows(
    flow_type: Optional[str] = None,
    uow_factory: Callable = Depends(get_uow_factory),
):
    """Retrieve traced execution flow paths."""
    with uow_factory() as uow:
        query = uow._session.query(CanonicalFlowModel)
        if flow_type:
            query = query.filter(CanonicalFlowModel.flow_type == flow_type)
        flows = query.all()
        return [
            CanonicalFlowResponse(
                id=str(f.id),
                flow_type=f.flow_type,
                source_entity_id=str(f.source_entity_id),
                target_entity_id=str(f.target_entity_id),
                intermediate_entities=[str(ie) for ie in f.intermediate_entities],
                confidence=float(f.confidence),
                metadata=f.metadata_,
                created_at=f.created_at
            )
            for f in flows
        ]

