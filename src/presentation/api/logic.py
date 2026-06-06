"""REST API endpoints for Phase 3 Behavioral Intelligence."""

from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases.extract_logic_use_case import ExtractLogicUseCase
from src.application.use_cases.get_entity_logic_use_case import GetEntityLogicUseCase
from src.application.use_cases.get_entity_logic_history_use_case import (
    GetEntityLogicHistoryUseCase,
)
from src.application.use_cases.get_behavior_evolution_use_case import (
    BehaviorEvolutionGraphResponse,
    GetBehaviorEvolutionUseCase,
)
from src.application.use_cases.get_logic_evidence_use_case import (
    GetLogicEvidenceUseCase,
)
from src.application.use_cases.get_behavior_explanation_use_case import (
    GetBehaviorExplanationUseCase,
)
from src.application.use_cases.get_behavior_drift_use_case import (
    GetBehaviorDriftUseCase,
)
from src.application.use_cases.validate_logic_use_case import (
    LogicValidationReport,
    ValidateLogicUseCase,
)
from src.presentation.schemas.logic_schemas import (
    BehaviorDriftSchema,
    BehaviorExplanationSchema,
    BehaviorEvolutionGraphSchema,
    LogicEvidenceSchema,
    LogicValidationReportSchema,
    LogicVersionSchema,
)
from src.presentation.dependencies import (
    get_extract_logic_use_case,
    get_get_entity_logic_use_case,
    get_get_entity_logic_history_use_case,
    get_get_behavior_evolution_use_case,
    get_get_logic_evidence_use_case,
    get_get_behavior_explanation_use_case,
    get_get_behavior_drift_use_case,
    get_validate_logic_use_case,
)

logic_router = APIRouter(prefix="/logic", tags=["logic"])


@logic_router.post("/extract", status_code=status.HTTP_202_ACCEPTED)
def extract_logic(
    repository_id: str,
    commit_hash: str,
    use_case: ExtractLogicUseCase = Depends(get_extract_logic_use_case),
):
    """Trigger logic extraction for all entities in a repository commit snapshot."""
    success = use_case.execute(repository_id, commit_hash)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Repository {repository_id} not found or snapshot missing.",
        )
    return {"status": "success", "message": "Logic extraction completed."}


@logic_router.get("/entity/{seid}", response_model=List[LogicVersionSchema])
def get_entity_logic(
    seid: str,
    commit_hash: str,
    use_case: GetEntityLogicUseCase = Depends(get_get_entity_logic_use_case),
):
    """Retrieve logic versions detected on a specific CodeEntity at a commit."""
    return use_case.execute(seid, commit_hash)


@logic_router.get("/entity/{seid}/history", response_model=List[LogicVersionSchema])
def get_entity_logic_history(
    seid: str,
    use_case: GetEntityLogicHistoryUseCase = Depends(
        get_get_entity_logic_history_use_case
    ),
):
    """Retrieve the chronological evolution history of logic for a CodeEntity."""
    return use_case.execute(seid)


@logic_router.get(
    "/signature/{signature_id}/evolution",
    response_model=BehaviorEvolutionGraphSchema,
)
def get_behavior_evolution(
    signature_id: str,
    use_case: GetBehaviorEvolutionUseCase = Depends(
        get_get_behavior_evolution_use_case
    ),
):
    """Retrieve the evolution graph of a logic signature (nodes/versions & edges/transitions)."""
    try:
        return use_case.execute(signature_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@logic_router.get(
    "/version/{version_id}/evidence", response_model=List[LogicEvidenceSchema]
)
def get_logic_evidence(
    version_id: str,
    use_case: GetLogicEvidenceUseCase = Depends(
        get_get_logic_evidence_use_case
    ),
):
    """Retrieve AST / flow evidence supporting a logic version detection."""
    return use_case.execute(version_id)


@logic_router.get(
    "/version/{version_id}/explanation", response_model=BehaviorExplanationSchema
)
def get_behavior_explanation(
    version_id: str,
    use_case: GetBehaviorExplanationUseCase = Depends(
        get_get_behavior_explanation_use_case
    ),
):
    """Retrieve explanation and rule verdicts for a logic version."""
    explanation = use_case.execute(version_id)
    if not explanation:
        raise HTTPException(
            status_code=404,
            detail=f"Explanation for logic version {version_id} not found.",
        )
    return explanation


@logic_router.get(
    "/transition/{transition_id}/drift", response_model=BehaviorDriftSchema
)
def get_behavior_drift(
    transition_id: str,
    use_case: GetBehaviorDriftUseCase = Depends(get_get_behavior_drift_use_case),
):
    """Retrieve drift scores and security crossing flags for a logic transition."""
    drift = use_case.execute(transition_id)
    if not drift:
        raise HTTPException(
            status_code=404,
            detail=f"Drift record for transition {transition_id} not found.",
        )
    return drift


@logic_router.get("/validate", response_model=LogicValidationReportSchema)
def validate_logic(
    use_case: ValidateLogicUseCase = Depends(get_validate_logic_use_case),
):
    """Run validation checks across logic signatures, versions, and transitions."""
    return use_case.execute()
