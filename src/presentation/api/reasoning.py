"""
Phase 7A — Reasoning API Router

Registers all REST endpoints for the Reasoning Intelligence Layer under:
    /api/v1/reasoning/

Endpoints
---------
POST  /reasoning/query
    Submit a natural-language reasoning question over the knowledge graph.
    Returns a fully auditable ReasoningResult.

GET   /reasoning/health
    Health check for the reasoning subsystem.

DELETE /reasoning/cache/{repository_id}
    Invalidate all cached reasoning results for a repository.

GET   /reasoning/cache/status
    Return the current number of cached entries.
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from src.presentation.schemas.reasoning_schemas import (
    ReasoningQueryRequest,
    ReasoningResultResponse,
    ReasoningHealthResponse,
    CacheStatusResponse,
    CacheInvalidationResponse,
)
from src.presentation.dependencies import (
    get_reasoning_query_engine,
    get_reasoning_cache,
    get_reasoning_strategy_registry,
)
from src.application.reasoning.reasoning_query_engine import ReasoningQueryEngine
from src.application.reasoning.reasoning_cache import ReasoningCache
from src.application.reasoning.reasoning_strategy_registry import ReasoningStrategyRegistry
from src.application.reasoning.reasoning_query_engine import REASONING_VERSION

logger = logging.getLogger(__name__)

reasoning_router = APIRouter(prefix="/reasoning", tags=["Reasoning Intelligence (Phase 7A)"])


def _result_to_response(result) -> ReasoningResultResponse:
    """Convert a ReasoningResult domain object to a Pydantic response schema."""
    data = result.to_dict()

    # Build nested schemas from the dict representation
    from src.presentation.schemas.reasoning_schemas import (
        ConfidenceSchema, LimitationSchema, HypothesisSchema,
        ReasoningStepSchema, ReasoningChainSchema,
        ProvenanceNodeSchema, ProvenanceEdgeSchema, ProvenanceGraphSchema,
        EvidenceSchema, SnapshotSchema,
    )
    from datetime import datetime

    conf = data.get("confidence", {})
    confidence_schema = ConfidenceSchema(
        score=conf.get("score", 0.0),
        level=conf.get("level", "MINIMAL"),
        rationale=conf.get("rationale", ""),
    )

    chain_data = data.get("reasoning_chain", {})
    steps = [
        ReasoningStepSchema(
            step_index=s.get("step_index", 0),
            step_type=s.get("step_type", ""),
            description=s.get("description", ""),
            inputs=s.get("inputs", []),
            outputs=s.get("outputs", []),
            executed_at=datetime.fromisoformat(s["executed_at"]) if s.get("executed_at") else datetime.utcnow(),
            duration_ms=s.get("duration_ms"),
        )
        for s in chain_data.get("steps", [])
    ]
    chain_schema = ReasoningChainSchema(
        execution_id=chain_data.get("execution_id", ""),
        total_steps=chain_data.get("total_steps", 0),
        steps=steps,
    )

    prov = data.get("provenance_graph", {})
    prov_nodes = [
        ProvenanceNodeSchema(
            node_id=n["node_id"], node_type=n["node_type"],
            label=n["label"], metadata=n.get("metadata", {}),
        )
        for n in prov.get("nodes", [])
    ]
    prov_edges = [
        ProvenanceEdgeSchema.model_validate(e)
        for e in prov.get("edges", [])
    ]
    prov_schema = ProvenanceGraphSchema(
        conclusion_id=prov.get("conclusion_id", ""),
        conclusion=prov.get("conclusion", ""),
        derived_from=prov.get("derived_from", []),
        nodes=prov_nodes,
        edges=prov_edges,
    )

    evidence_schemas = [
        EvidenceSchema(
            source_id=e["source_id"],
            source_type=e["source_type"],
            description=e["description"],
            weight=e["weight"],
            validated=e["validated"],
            metadata=e.get("metadata", {}),
        )
        for e in data.get("evidence", [])
    ]

    def _hyp_schema(h: dict) -> HypothesisSchema:
        return HypothesisSchema(
            hypothesis_id=h["hypothesis_id"],
            statement=h["statement"],
            supporting_ids=h.get("supporting_ids", []),
            contradicting_ids=h.get("contradicting_ids", []),
            score=h.get("score", 0.0),
            is_selected=h.get("is_selected", False),
            rationale=h.get("rationale", ""),
        )

    sel_hyp = None
    if data.get("selected_hypothesis"):
        sel_hyp = _hyp_schema(data["selected_hypothesis"])

    alt_hyps = [_hyp_schema(h) for h in data.get("alternative_hypotheses", [])]

    limitations = [
        LimitationSchema(
            reason=lim["reason"],
            affected_area=lim["affected_area"],
            impact=lim["impact"],
        )
        for lim in data.get("limitations", [])
    ]

    snapshot_schema = None
    if data.get("snapshot"):
        s = data["snapshot"]
        snapshot_schema = SnapshotSchema(
            repository_id=s["repository_id"],
            commit_hash=s["commit_hash"],
            capability_version=s["capability_version"],
            ontology_version=s["ontology_version"],
            compiler_version=s["compiler_version"],
            reasoning_version=s["reasoning_version"],
            snapshot_at=datetime.fromisoformat(s["snapshot_at"]),
        )

    generated_at_raw = data.get("generated_at", "")
    generated_at = (
        datetime.fromisoformat(generated_at_raw)
        if generated_at_raw
        else datetime.utcnow()
    )

    return ReasoningResultResponse(
        execution_id=data["execution_id"],
        question=data["question"],
        answer=data["answer"],
        confidence=confidence_schema,
        reasoning_chain=chain_schema,
        provenance_graph=prov_schema,
        evidence=evidence_schemas,
        selected_hypothesis=sel_hyp,
        alternative_hypotheses=alt_hyps,
        limitations=limitations,
        generated_at=generated_at,
        source_ids=data.get("source_ids", []),
        snapshot=snapshot_schema,
    )


@reasoning_router.post(
    "/query",
    response_model=ReasoningResultResponse,
    summary="Ask a reasoning question",
    description=(
        "Submit a natural-language question about the codebase. "
        "Returns a fully auditable ReasoningResult with evidence provenance, "
        "hypothesis ranking, limitations, and a step-by-step reasoning chain."
    ),
    status_code=status.HTTP_200_OK,
)
def reasoning_query(
    request: ReasoningQueryRequest,
    engine: ReasoningQueryEngine = Depends(get_reasoning_query_engine),
) -> ReasoningResultResponse:
    """Execute a Phase 7A reasoning query."""
    try:
        result = engine.query(
            repository_id=request.repository_id,
            commit_hash=request.commit_hash,
            query=request.query,
            capability_version=request.capability_version,
            ontology_version=request.ontology_version,
            compiler_version=request.compiler_version,
            use_cache=request.use_cache,
        )
        return _result_to_response(result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("Reasoning query failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reasoning pipeline error: {str(exc)[:200]}",
        ) from exc


@reasoning_router.get(
    "/health",
    response_model=ReasoningHealthResponse,
    summary="Reasoning engine health check",
)
def reasoning_health(
    cache: ReasoningCache = Depends(get_reasoning_cache),
    registry: ReasoningStrategyRegistry = Depends(get_reasoning_strategy_registry),
) -> ReasoningHealthResponse:
    """Return the health status of the reasoning subsystem."""
    registered = [qt.value for qt in registry.registered_types()]
    return ReasoningHealthResponse(
        status="ok",
        reasoning_version=REASONING_VERSION,
        cache_size=cache.size(),
        registered_strategies=registered,
    )


@reasoning_router.delete(
    "/cache/{repository_id}",
    response_model=CacheInvalidationResponse,
    summary="Invalidate reasoning cache for a repository",
    description=(
        "Removes all cached reasoning results for the given repository. "
        "Call this after ingesting a new commit or recomputing capabilities."
    ),
)
def invalidate_cache(
    repository_id: str,
    cache: ReasoningCache = Depends(get_reasoning_cache),
) -> CacheInvalidationResponse:
    """Invalidate all cached reasoning results for a repository."""
    removed = cache.invalidate(repository_id)
    return CacheInvalidationResponse(
        repository_id=repository_id,
        entries_removed=removed,
        message=f"Removed {removed} cached reasoning result(s) for repository {repository_id}.",
    )


@reasoning_router.get(
    "/cache/status",
    response_model=CacheStatusResponse,
    summary="Get reasoning cache size",
)
def cache_status(
    cache: ReasoningCache = Depends(get_reasoning_cache),
) -> CacheStatusResponse:
    """Return the current number of cached reasoning results."""
    size = cache.size()
    return CacheStatusResponse(
        cache_size=size,
        message=f"Reasoning cache currently holds {size} result(s).",
    )
