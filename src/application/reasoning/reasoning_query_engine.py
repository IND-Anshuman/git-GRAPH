"""
Phase 7A — ReasoningQueryEngine

The primary orchestrator facade for the Reasoning Intelligence Layer.

It wires together all Phase 7A engines in the correct pipeline order:

    1. Cache check  →  return cached result immediately if available
    2. QueryPlanner  →  classify question and produce QueryPlan
    3. ReasoningSnapshot  →  record graph state at execution time
    4. EvidenceCollectionEngine  →  fetch targeted evidence from UoW
    5. EvidenceExpansionEngine   →  multi-hop neighbour traversal
    6. EvidenceValidationLayer   →  hallucination prevention gate
    7. HypothesisGenerationEngine  →  produce competing explanations
    8. HypothesisScoringEngine     →  rank and select best hypothesis
    9. ReasoningStrategyRegistry.resolve().execute()  →  strategy-specific reasoning
   10. ReasoningArtifactService  →  persist result as KnowledgeArtifact
   11. ReasoningCache.put()  →  cache for future identical queries

The orchestrator NEVER contains if/elif question-type logic — that belongs
exclusively in concrete ``IReasoningStrategy`` implementations.

Usage::

    engine = ReasoningQueryEngine(
        strategy_registry=ReasoningStrategyRegistry.default(),
        cache=ReasoningCache(),
        uow_factory=lambda: SQLAlchemyUnitOfWork(session_factory),
    )
    result = engine.query(
        repository_id="...",
        commit_hash="abc1234",
        query="Why is AuthService critical?",
    )
"""

from __future__ import annotations

import uuid
import logging
from datetime import datetime
from typing import Callable

from src.application.reasoning.reasoning_question_type import ReasoningQuestionType
from src.application.reasoning.reasoning_snapshot import ReasoningSnapshot
from src.application.reasoning.reasoning_context import ReasoningContext
from src.application.reasoning.reasoning_chain import ReasoningChain
from src.application.reasoning.reasoning_result import ReasoningResult
from src.application.reasoning.reasoning_confidence import ReasoningConfidence
from src.application.reasoning.reasoning_limitations import ReasoningLimitation
from src.application.reasoning.evidence_provenance_graph import EvidenceProvenanceGraph
from src.application.reasoning.query_planner import QueryPlanner
from src.application.reasoning.evidence_collection_engine import EvidenceCollectionEngine
from src.application.reasoning.evidence_expansion_engine import EvidenceExpansionEngine
from src.application.reasoning.evidence_validation_layer import EvidenceValidationLayer
from src.application.reasoning.hypothesis_generation_engine import HypothesisGenerationEngine
from src.application.reasoning.hypothesis_scoring_engine import HypothesisScoringEngine
from src.application.reasoning.reasoning_strategy_registry import ReasoningStrategyRegistry
from src.application.reasoning.reasoning_cache import ReasoningCache
from src.application.reasoning.reasoning_artifact_service import ReasoningArtifactService
from src.application.ports.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)

REASONING_VERSION = "7A.0"


class ReasoningQueryEngine:
    """Primary orchestrator for Phase 7A deterministic graph reasoning.

    All engines are injected at construction so they can be individually
    mocked or swapped without modifying this class.

    Args:
        strategy_registry:   ``ReasoningStrategyRegistry`` instance.
        cache:               ``ReasoningCache`` instance (shared across requests).
        uow_factory:         Callable that returns an open :class:`IUnitOfWork`.
        artifact_service:    ``ReasoningArtifactService`` instance.
        persist_artifacts:   Whether to persist results as KnowledgeArtifacts
                             (default: True).  Disable in tests.
    """

    def __init__(
        self,
        strategy_registry: ReasoningStrategyRegistry,
        cache: ReasoningCache,
        uow_factory: Callable[[], IUnitOfWork],
        artifact_service: ReasoningArtifactService | None = None,
        persist_artifacts: bool = True,
    ) -> None:
        self._strategy_registry = strategy_registry
        self._cache = cache
        self._uow_factory = uow_factory
        self._artifact_service = artifact_service or ReasoningArtifactService()
        self._persist_artifacts = persist_artifacts

        # Pipeline stage engines
        self._planner = QueryPlanner()
        self._collector = EvidenceCollectionEngine()
        self._expander = EvidenceExpansionEngine()
        self._validator = EvidenceValidationLayer()
        self._generator = HypothesisGenerationEngine()
        self._scorer = HypothesisScoringEngine()

    # ── Public API ────────────────────────────────────────────────────────────

    def query(
        self,
        repository_id: str,
        commit_hash: str,
        query: str,
        capability_version: str = "unknown",
        ontology_version: str = "unknown",
        compiler_version: str = "unknown",
        use_cache: bool = True,
    ) -> ReasoningResult:
        """Execute a reasoning query and return the full auditable result.

        Args:
            repository_id:      Target repository UUID string.
            commit_hash:        Current HEAD commit hash (used for cache key).
            query:              Natural-language question from the user.
            capability_version: Version hash of the capability graph.
            ontology_version:   Version hash of the concept/ontology graph.
            compiler_version:   Semantic compiler version string.
            use_cache:          Whether to check / populate the cache.

        Returns:
            A fully populated :class:`ReasoningResult`.
        """
        execution_id = str(uuid.uuid4())
        logger.info(
            "ReasoningQueryEngine.query: execution_id=%s repo=%r query=%r",
            execution_id,
            repository_id,
            query[:120],
        )

        # ── 1. Query planning ────────────────────────────────────────────────
        plan = self._planner.plan(query)

        # ── 2. Cache check ───────────────────────────────────────────────────
        if use_cache:
            cache_key = ReasoningCache.make_key(
                repository_id, commit_hash, plan.question_type, query
            )
            cached = self._cache.get(cache_key)
            if cached is not None:
                logger.info(
                    "ReasoningQueryEngine: cache HIT for execution_id=%s", execution_id
                )
                return cached
        else:
            cache_key = None  # type: ignore[assignment]

        # ── 3. Snapshot ──────────────────────────────────────────────────────
        snapshot = ReasoningSnapshot(
            repository_id=repository_id,
            commit_hash=commit_hash,
            capability_version=capability_version,
            ontology_version=ontology_version,
            compiler_version=compiler_version,
            reasoning_version=REASONING_VERSION,
            snapshot_at=datetime.utcnow(),
        )

        # ── 4. Build context ──────────────────────────────────────────────────
        context = ReasoningContext(
            execution_id=execution_id,
            repository_id=repository_id,
            query=query,
            question_type=plan.question_type,
            snapshot=snapshot,
            chain=ReasoningChain(execution_id=execution_id),
        )
        context.chain.add_step(
            step_type="query_planning",
            description=(
                f"QueryPlanner classified question_type={plan.question_type.value}, "
                f"target={plan.target_term!r}, scopes={plan.collect_scopes}, "
                f"max_hops={plan.max_hops}."
            ),
        )

        # ── 5–9. Pipeline ─────────────────────────────────────────────────────
        with self._uow_factory() as uow:
            try:
                # 5. Evidence collection
                self._collector.collect(context, plan, uow)

                # 6. Evidence expansion
                self._expander.expand(context, uow, max_hops=plan.max_hops)

                # 7. Evidence validation (hallucination prevention)
                self._validator.validate(context, uow)

                # 8. Hypothesis generation
                self._generator.generate(context)

                # 9. Hypothesis scoring
                self._scorer.score(context)

                # 10. Strategy execution
                strategy = self._strategy_registry.resolve(plan.question_type)
                context.chain.add_step(
                    step_type="strategy_resolution",
                    description=f"Resolved strategy: {type(strategy).__name__}",
                )
                result = strategy.execute(context)

                # 11. Persist artifact
                if self._persist_artifacts:
                    try:
                        self._artifact_service.save(result, uow)
                        uow.commit()
                    except Exception as persist_exc:  # noqa: BLE001
                        logger.warning(
                            "Artifact persistence failed for execution_id=%s: %s",
                            execution_id,
                            persist_exc,
                        )

            except Exception as exc:
                logger.error(
                    "ReasoningQueryEngine pipeline failed for execution_id=%s: %s",
                    execution_id,
                    exc,
                )
                result = self._build_error_result(execution_id, query, snapshot, str(exc))

        # ── 12. Cache store ────────────────────────────────────────────────────
        if use_cache and cache_key is not None:
            self._cache.put(cache_key, result)

        return result

    # ── Error handling ────────────────────────────────────────────────────────

    def _build_error_result(
        self,
        execution_id: str,
        query: str,
        snapshot: ReasoningSnapshot,
        error_message: str,
    ) -> ReasoningResult:
        """Build a minimal result that signals a pipeline failure."""
        from src.application.reasoning.reasoning_hypothesis import ReasoningHypothesis

        chain = ReasoningChain(execution_id=execution_id)
        chain.add_step(
            step_type="error",
            description=f"Pipeline failed: {error_message[:200]}",
        )
        return ReasoningResult(
            execution_id=execution_id,
            question=query,
            answer=f"Reasoning pipeline encountered an error: {error_message[:200]}",
            confidence=ReasoningConfidence.from_score(
                0.0, "Pipeline error — result is unreliable."
            ),
            reasoning_chain=chain,
            provenance_graph=EvidenceProvenanceGraph.empty(
                conclusion_id=f"error_{execution_id}",
                conclusion="Pipeline error",
            ),
            evidence=[],
            selected_hypothesis=None,
            limitations=[
                ReasoningLimitation(
                    reason=f"Pipeline error: {error_message[:100]}",
                    affected_area="all",
                    impact="Result is unavailable — please retry or check logs.",
                )
            ],
            generated_at=datetime.utcnow(),
            source_ids=[],
            snapshot=snapshot,
        )
