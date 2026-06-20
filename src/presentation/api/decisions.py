"""
Phase 7C — Decision Intelligence Layer REST API

All endpoints follow the platform conventions:
    - GET /repositories/{repository_id}/decisions/...
    - Dependency injection via FastAPI Depends()
    - Response models are typed Pydantic schemas
    - 404 errors use standard HTTPException
    - 422 errors are raised for invalid filter parameters
    - All endpoints include OpenAPI descriptions

Routes:
    GET  /repositories/{id}/decisions                  List all decisions
    GET  /repositories/{id}/decisions/summary          Portfolio summary
    GET  /repositories/{id}/decisions/active           Active decisions only
    GET  /repositories/{id}/decisions/search           Full-text + filter search
    GET  /repositories/{id}/decisions/timeline         Evolution timeline
    GET  /repositories/{id}/decisions/lifecycles       Technology lifecycles
    GET  /repositories/{id}/decisions/graph            Decision dependency graph
    GET  /repositories/{id}/decisions/conflicts        All conflicts
    GET  /repositories/{id}/decisions/intents          Inferred intents
    GET  /repositories/{id}/decisions/causal-chains    Causal reasoning chains

    GET  /decisions/{decision_id}                      Single decision (detail)
    GET  /decisions/{decision_id}/versions             Version history
    GET  /decisions/{decision_id}/fitness              Fitness evaluation
    GET  /decisions/{decision_id}/conflicts            Decision-level conflicts
    GET  /decisions/{decision_id}/causal               Causal relationships for this decision

    GET  /intents/{intent_id}                          Single intent detail
"""

from __future__ import annotations

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.presentation.dependencies import get_uow_factory
from src.presentation.schemas.decision_schemas import (
    CausalChainSchema,
    CausalRelationshipSchema,
    DecisionConflictSchema,
    DecisionDetailSchema,
    DecisionFitnessSchema,
    DecisionGraphSchema,
    DecisionSchema,
    DecisionSummarySchema,
    DecisionVersionSchema,
    IntentSchema,
    TechnologyLifecycleSchema,
)
from src.application.decision_intelligence.decision_query_engine import DecisionQueryEngine
from src.application.decision_intelligence.decision_fitness_engine import DecisionFitnessEngine
from src.application.decision_intelligence.decision_evolution_engine import DecisionEvolutionEngine
from src.application.decision_intelligence.technology_lifecycle_engine import TechnologyLifecycleEngine
from src.application.decision_intelligence.decision_graph import DecisionGraph
from src.application.decision_intelligence.decision_status import DecisionStatus
from src.application.decision_intelligence.decision_type import DecisionType

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Decision Intelligence Layer (Phase 7C)"])

# ─── Dependency helpers ───────────────────────────────────────────────────────

def _get_query_engine(uow_factory) -> DecisionQueryEngine:
    uow = uow_factory()
    return DecisionQueryEngine(uow)


def _schema_from_decision_row(row) -> DecisionSchema:
    """Convert an ORM row to a DecisionSchema."""
    return DecisionSchema(
        id=row.id,
        name=row.name,
        description=row.description or "",
        decision_type=row.decision_type,
        status=row.status,
        confidence_score=row.confidence_score,
        first_seen_commit=row.first_seen_commit,
        last_seen_commit=row.last_seen_commit,
        repository_id=row.repository_id,
        created_at=row.created_at,
        updated_at=getattr(row, "updated_at", None),
    )


def _schema_from_version_row(row) -> DecisionVersionSchema:
    return DecisionVersionSchema(
        id=str(row.id),
        decision_id=str(row.decision_id),
        version=row.version,
        commit_hash=row.commit_hash,
        confidence=row.confidence,
        supporting_evidence=row.supporting_evidence,
        generated_at=row.generated_at,
    )


def _schema_from_conflict_row(row) -> DecisionConflictSchema:
    return DecisionConflictSchema(
        id=str(row.id),
        decision_a_id=str(row.decision_a_id),
        decision_b_id=str(row.decision_b_id),
        conflict_type=row.conflict_type,
        description=row.description,
        severity=row.severity,
        detected_at=row.detected_at,
    )


def _schema_from_intent_row(row) -> IntentSchema:
    return IntentSchema(
        id=row.id,
        name=row.name or "",
        intent_type=row.intent_type,
        description=row.description,
        confidence_score=row.confidence_score,
        supporting_decisions=row.supporting_decisions,
        repository_id=row.repository_id,
        first_seen_at=row.first_seen_at,
        last_seen_at=row.last_seen_at,
    )


def _schema_from_causal_row(row) -> CausalRelationshipSchema:
    return CausalRelationshipSchema(
        id=str(row.id),
        chain_id=str(row.chain_id) if row.chain_id else None,
        cause_id=str(row.cause_id),
        effect_id=str(row.effect_id),
        cause_label=row.cause_label,
        effect_label=row.effect_label,
        relationship_type=row.relationship_type,
        confidence=row.confidence,
        evidence=row.evidence,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Repository-scoped endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/repositories/{repository_id}/decisions",
    response_model=List[DecisionSchema],
    summary="List all decisions for a repository",
    description=(
        "Returns all architectural decisions discovered for the given repository, "
        "ordered by creation date (newest first)."
    ),
)
def list_decisions(
    repository_id: str,
    uow_factory=Depends(get_uow_factory),
):
    engine = _get_query_engine(uow_factory)
    try:
        rows = engine.get_all_decisions(repository_id)
        return [_schema_from_decision_row(r) for r in rows]
    except Exception as exc:
        logger.exception("list_decisions failed for repo=%s", repository_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get(
    "/repositories/{repository_id}/decisions/summary",
    response_model=DecisionSummarySchema,
    summary="Decision portfolio summary",
    description=(
        "Returns a high-level portfolio summary: total decisions, intents, "
        "breakdown by type and status, and average confidence score."
    ),
)
def get_decision_summary(
    repository_id: str,
    uow_factory=Depends(get_uow_factory),
):
    engine = _get_query_engine(uow_factory)
    try:
        summary = engine.get_decision_summary(repository_id)
        return DecisionSummarySchema(**summary)
    except Exception as exc:
        logger.exception("get_decision_summary failed for repo=%s", repository_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get(
    "/repositories/{repository_id}/decisions/active",
    response_model=List[DecisionSchema],
    summary="List active decisions",
    description="Returns only decisions with status=ACTIVE — the current decision baseline.",
)
def list_active_decisions(
    repository_id: str,
    uow_factory=Depends(get_uow_factory),
):
    engine = _get_query_engine(uow_factory)
    rows = engine.get_active_decisions(repository_id)
    return [_schema_from_decision_row(r) for r in rows]


@router.get(
    "/repositories/{repository_id}/decisions/search",
    response_model=List[DecisionSchema],
    summary="Search decisions with filters",
    description=(
        "Full-text search over decision names and descriptions. "
        "Optionally filter by decision_type, status, and minimum confidence."
    ),
)
def search_decisions(
    repository_id: str,
    q: str = Query(default="", description="Search term (case-insensitive substring match)"),
    decision_type: Optional[str] = Query(default=None, description="Filter by DecisionType enum value"),
    status: Optional[str] = Query(default=None, description="Filter by DecisionStatus enum value"),
    min_confidence: float = Query(default=0.0, ge=0.0, le=1.0, description="Minimum confidence score"),
    uow_factory=Depends(get_uow_factory),
):
    dtype = None
    dstatus = None
    try:
        if decision_type:
            dtype = DecisionType(decision_type)
        if status:
            dstatus = DecisionStatus(status)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    engine = _get_query_engine(uow_factory)
    rows = engine.search_decisions(repository_id, q, dtype, dstatus, min_confidence)
    return [_schema_from_decision_row(r) for r in rows]


@router.get(
    "/repositories/{repository_id}/decisions/conflicts",
    response_model=List[DecisionConflictSchema],
    summary="All decision conflicts in a repository",
    description="Returns all detected conflicts between decisions in the repository.",
)
def list_all_conflicts(
    repository_id: str,
    uow_factory=Depends(get_uow_factory),
):
    engine = _get_query_engine(uow_factory)
    rows = engine.get_all_conflicts(repository_id)
    return [_schema_from_conflict_row(r) for r in rows]


@router.get(
    "/repositories/{repository_id}/decisions/intents",
    response_model=List[IntentSchema],
    summary="Inferred strategic intents",
    description=(
        "Returns all strategic intents inferred for the repository. "
        "Intents represent the 'Why' behind groups of decisions."
    ),
)
def list_intents(
    repository_id: str,
    uow_factory=Depends(get_uow_factory),
):
    engine = _get_query_engine(uow_factory)
    rows = engine.get_intents(repository_id)
    return [_schema_from_intent_row(r) for r in rows]


@router.get(
    "/repositories/{repository_id}/decisions/causal-chains",
    response_model=List[CausalRelationshipSchema],
    summary="Causal reasoning chains",
    description=(
        "Returns all causal relationships (MOTIVATES, ENABLES, CONTRADICTS) "
        "between intents and decisions for a repository."
    ),
)
def list_causal_chains(
    repository_id: str,
    uow_factory=Depends(get_uow_factory),
):
    engine = _get_query_engine(uow_factory)
    rows = engine.get_causal_chains(repository_id)
    return [_schema_from_causal_row(r) for r in rows]


@router.get(
    "/repositories/{repository_id}/decisions/graph",
    response_model=DecisionGraphSchema,
    summary="Decision dependency graph",
    description=(
        "Returns the decision dependency graph as an adjacency list (nodes + edges). "
        "Suitable for graph visualisation or further analysis."
    ),
)
def get_decision_graph(
    repository_id: str,
    uow_factory=Depends(get_uow_factory),
):
    from src.application.decision_intelligence.decision_graph import DecisionGraph

    engine = _get_query_engine(uow_factory)
    decision_rows = engine.get_all_decisions(repository_id)

    # We need real Decision objects (domain) to build the graph.
    # For now, build lightweight graph from ORM rows by treating rows as objects.
    # In a full pipeline, DecisionDiscoveryEngine results are passed here.
    # The graph edges come from decision_dependencies table.
    from src.application.decision_intelligence.decision import Decision
    from src.application.decision_intelligence.decision_confidence import DecisionConfidence
    from src.application.decision_intelligence.decision_evidence import DecisionEvidence
    from src.application.decision_intelligence.decision_type import DecisionType
    from src.application.decision_intelligence.decision_status import DecisionStatus
    import uuid
    from datetime import datetime, timezone

    decisions = []
    for row in decision_rows:
        try:
            d = Decision(
                id=uuid.UUID(str(row.id)),
                name=row.name,
                description=row.description or "",
                decision_type=DecisionType(row.decision_type),
                confidence=DecisionConfidence.compute(
                    evidence_coverage=row.confidence_score or 0.5,
                    historical_support=0.5,
                    architectural_support=0.3,
                    capability_support=0.3,
                    artifact_agreement=0.2,
                ),
                status=DecisionStatus(row.status),
                created_at=row.created_at or datetime.now(timezone.utc),
                first_seen_commit=row.first_seen_commit or "",
                last_seen_commit=row.last_seen_commit or "",
                repository_id=row.repository_id,
                supporting_evidence=DecisionEvidence(),
            )
            decisions.append(d)
        except (ValueError, TypeError):
            continue

    # Build graph with empty dependency list (dependency edges from DB in future)
    graph = DecisionGraph(decisions=decisions, dependencies=[])
    adjacency = graph.to_adjacency_dict()

    from src.presentation.schemas.decision_schemas import DecisionGraphNodeSchema, DecisionGraphEdgeSchema
    return DecisionGraphSchema(
        nodes=[DecisionGraphNodeSchema(**n) for n in adjacency["nodes"]],
        edges=[DecisionGraphEdgeSchema(**e) for e in adjacency["edges"]],
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Single-decision endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/decisions/{decision_id}",
    response_model=DecisionDetailSchema,
    summary="Get decision detail",
    description=(
        "Returns full detail for a single decision: versions, evidence, "
        "fitness evaluation, and conflicts."
    ),
)
def get_decision(
    decision_id: str,
    uow_factory=Depends(get_uow_factory),
):
    engine = _get_query_engine(uow_factory)
    row = engine.get_decision_by_id(decision_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Decision '{decision_id}' not found")

    # Fetch related records
    versions = engine.get_decision_versions(decision_id)
    conflicts = engine.get_decision_conflicts(decision_id)
    fitness_row = engine.get_decision_fitness(decision_id)

    return DecisionDetailSchema(
        id=row.id,
        name=row.name,
        description=row.description or "",
        decision_type=row.decision_type,
        status=row.status,
        confidence_score=row.confidence_score,
        first_seen_commit=row.first_seen_commit,
        last_seen_commit=row.last_seen_commit,
        repository_id=row.repository_id,
        created_at=row.created_at,
        updated_at=getattr(row, "updated_at", None),
        versions=[_schema_from_version_row(v) for v in versions],
        conflicts=[_schema_from_conflict_row(c) for c in conflicts],
        fitness=DecisionFitnessSchema.model_validate(fitness_row) if fitness_row else None,
        evidence=None,
    )


@router.get(
    "/decisions/{decision_id}/versions",
    response_model=List[DecisionVersionSchema],
    summary="Decision version history",
    description="Returns all recorded versions for a decision, ordered by version number ascending.",
)
def get_decision_versions(
    decision_id: str,
    uow_factory=Depends(get_uow_factory),
):
    engine = _get_query_engine(uow_factory)
    decision = engine.get_decision_by_id(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision '{decision_id}' not found")
    versions = engine.get_decision_versions(decision_id)
    return [_schema_from_version_row(v) for v in versions]


@router.get(
    "/decisions/{decision_id}/fitness",
    response_model=DecisionFitnessSchema,
    summary="Decision fitness evaluation",
    description=(
        "Returns the latest fitness evaluation for a decision, including longevity, "
        "stability, impact, adoption, success rate, and overall fitness rating."
    ),
)
def get_decision_fitness(
    decision_id: str,
    uow_factory=Depends(get_uow_factory),
):
    engine = _get_query_engine(uow_factory)
    decision = engine.get_decision_by_id(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision '{decision_id}' not found")

    fitness_row = engine.get_decision_fitness(decision_id)
    if not fitness_row:
        raise HTTPException(
            status_code=404,
            detail=f"No fitness evaluation found for decision '{decision_id}'. "
                   f"Run a discovery scan first.",
        )
    return DecisionFitnessSchema.from_orm_with_rating(fitness_row)


@router.get(
    "/decisions/{decision_id}/conflicts",
    response_model=List[DecisionConflictSchema],
    summary="Conflicts for a specific decision",
    description="Returns all known conflicts that involve the specified decision.",
)
def get_decision_conflicts(
    decision_id: str,
    uow_factory=Depends(get_uow_factory),
):
    engine = _get_query_engine(uow_factory)
    decision = engine.get_decision_by_id(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision '{decision_id}' not found")

    rows = engine.get_decision_conflicts(decision_id)
    return [_schema_from_conflict_row(r) for r in rows]


@router.get(
    "/decisions/{decision_id}/causal",
    response_model=List[CausalRelationshipSchema],
    summary="Causal relationships for a decision",
    description=(
        "Returns all causal relationships where this decision appears as either "
        "cause or effect. Includes MOTIVATES, ENABLES, and CONTRADICTS edges."
    ),
)
def get_decision_causal_relationships(
    decision_id: str,
    uow_factory=Depends(get_uow_factory),
):
    engine = _get_query_engine(uow_factory)
    decision = engine.get_decision_by_id(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision '{decision_id}' not found")

    # Look for both cause and effect relationships
    with uow_factory() as uow:
        cause_rows = uow.causal_relationships.get_by_cause_id(decision_id)
        effect_rows = uow.causal_relationships.get_by_effect_id(decision_id)
    all_rows = list({str(r.id): r for r in cause_rows + effect_rows}.values())
    return [_schema_from_causal_row(r) for r in all_rows]


# ─────────────────────────────────────────────────────────────────────────────
#  Intent endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/intents/{intent_id}",
    response_model=IntentSchema,
    summary="Get intent detail",
    description="Returns full detail for a single strategic intent.",
)
def get_intent(
    intent_id: str,
    uow_factory=Depends(get_uow_factory),
):
    engine = _get_query_engine(uow_factory)
    row = engine.get_intent_by_id(intent_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Intent '{intent_id}' not found")
    return _schema_from_intent_row(row)
