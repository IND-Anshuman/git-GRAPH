"""
Phase 7A — ReasoningStrategyRegistry + Concrete Phase 7A Strategies

The registry is the central dispatch table for all reasoning strategies.
``ReasoningQueryEngine`` calls ``registry.resolve(question_type)`` and
receives the correct strategy without any if/elif logic.

Concrete strategies implemented here (Phase 7A)
------------------------------------------------
  WhyStrategy          – answers "Why does X exist / behave this way?"
  RootCauseStrategy    – answers "What is the root cause of Y?"
  BlastRadiusStrategy  – answers "What breaks if X changes / fails?"
  CounterfactualStrategy – answers "What would happen if we changed X?"
  ArchitectureStrategy – answers "What are the architectural patterns?"

Phase 7B/7C strategies are registered by calling
``registry.register(DriftStrategy())`` from the DI container — the
orchestrator never changes.

Strategy execution contract
----------------------------
Every strategy *must*:
  1. Add at least one step to ``context.chain``.
  2. Produce a ``ReasoningResult`` with all required fields populated.
  3. Never make LLM calls (Phase 7A is purely deterministic).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from src.application.reasoning.reasoning_question_type import ReasoningQuestionType
from src.application.reasoning.reasoning_strategy import IReasoningStrategy
from src.application.reasoning.reasoning_context import ReasoningContext
from src.application.reasoning.reasoning_result import ReasoningResult
from src.application.reasoning.reasoning_confidence import ReasoningConfidence
from src.application.reasoning.reasoning_chain import ReasoningChain
from src.application.reasoning.evidence_provenance_graph import (
    EvidenceProvenanceGraph,
    ProvenanceNode,
    ProvenanceEdge,
)
from src.application.reasoning.reasoning_hypothesis import ReasoningHypothesis
from src.application.reasoning.reasoning_limitations import ReasoningLimitation
from src.application.reasoning.evidence_weight_registry import EvidenceWeightRegistry


# ── Shared helper ─────────────────────────────────────────────────────────────

def _build_provenance(context: ReasoningContext, conclusion: str) -> EvidenceProvenanceGraph:
    """Build a provenance graph from all validated evidence in *context*."""
    conclusion_id = f"conclusion_{context.execution_id}"
    graph = EvidenceProvenanceGraph(conclusion_id=conclusion_id, conclusion=conclusion)

    conclusion_node = ProvenanceNode(
        node_id=conclusion_id,
        node_type="conclusion",
        label=conclusion[:120],
    )
    graph.add_node(conclusion_node)

    for ev in context.validated_evidence:
        ev_node = ProvenanceNode(
            node_id=ev.source_id,
            node_type=ev.source_type,
            label=ev.description[:120],
        )
        graph.add_node(ev_node)
        graph.add_edge(ProvenanceEdge(
            from_id=ev.source_id,
            to_id=conclusion_id,
            relationship="derived_from",
        ))

    return graph


def _make_result(
    context: ReasoningContext,
    answer: str,
    hypothesis_statement: str,
    supporting_ids: list[str],
) -> ReasoningResult:
    """Assemble a complete ReasoningResult from the context and strategy outputs."""
    evidence_types = context.all_collected_source_types()
    confidence = ReasoningConfidence.compute(
        weights=EvidenceWeightRegistry.all_weights(),
        found_types=evidence_types,
        rationale=f"Evidence coverage across {len(context.validated_evidence)} validated nodes.",
    )

    hypothesis_id = str(uuid.uuid4())
    selected = ReasoningHypothesis(
        hypothesis_id=hypothesis_id,
        statement=hypothesis_statement,
        supporting_ids=supporting_ids,
        score=confidence.score,
        is_selected=True,
        rationale=confidence.rationale,
    )

    provenance = _build_provenance(context, answer)

    return ReasoningResult(
        execution_id=context.execution_id,
        question=context.query,
        answer=answer,
        confidence=confidence,
        reasoning_chain=context.chain,
        provenance_graph=provenance,
        evidence=list(context.validated_evidence),
        selected_hypothesis=selected,
        alternative_hypotheses=list(context.hypotheses),
        limitations=_detect_limitations(context),
        generated_at=datetime.utcnow(),
        source_ids=context.source_ids(),
        snapshot=context.snapshot,
    )


def _detect_limitations(context: ReasoningContext) -> list[ReasoningLimitation]:
    """Auto-detect common limitations from missing evidence categories."""
    limitations: list[ReasoningLimitation] = []
    types = context.all_collected_source_types()

    if "ownership" not in types:
        limitations.append(ReasoningLimitation(
            reason="Ownership data unavailable — no CODEOWNERS or ownership metadata found.",
            affected_area="ownership",
            impact="Cannot attribute responsibility; ownership conclusions are absent.",
        ))
    if "timeline" not in types:
        limitations.append(ReasoningLimitation(
            reason="Historical timeline not collected for this query.",
            affected_area="evolution",
            impact="Temporal / evolutionary reasoning is limited to current snapshot.",
        ))
    if not context.capabilities:
        limitations.append(ReasoningLimitation(
            reason="No capability data found for this repository.",
            affected_area="capability",
            impact="Capability-level reasoning is absent; lower confidence expected.",
        ))
    return limitations


# ── Concrete strategies ───────────────────────────────────────────────────────

class WhyStrategy:
    """Answers causal 'Why does X exist / behave this way?' questions."""

    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.WHY

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="why_strategy",
            description="WhyStrategy: analysing entity purpose from capabilities and concepts.",
            inputs=context.source_ids(),
        )

        capability_names = [
            cap.get("name", cap.get("id", "unknown"))
            for cap in context.capabilities[:5]
        ]
        concept_names = [
            c.get("name", c.get("id", "unknown"))
            for c in context.concepts[:5]
        ]

        if capability_names:
            answer = (
                f"Based on {len(context.validated_evidence)} evidence nodes, "
                f"the subject exists to support capabilities: {', '.join(capability_names)}."
            )
            if concept_names:
                answer += f" It implements concepts: {', '.join(concept_names)}."
        else:
            answer = (
                "Insufficient capability data to fully explain purpose. "
                "The subject is referenced in the knowledge graph but no compiled "
                "capability context was found."
            )

        return _make_result(
            context,
            answer=answer,
            hypothesis_statement=f"The subject exists to support: {', '.join(capability_names or ['unknown'])}.",
            supporting_ids=context.source_ids(),
        )


class RootCauseStrategy:
    """Answers 'What is the root cause of incident / anomaly Y?' questions."""

    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.ROOT_CAUSE

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="root_cause_strategy",
            description="RootCauseStrategy: tracing dependency chain for root cause.",
            inputs=context.source_ids(),
        )

        dep_count = len(context.relationships)
        entity_count = len(context.entities)

        answer = (
            f"Root cause analysis identified {dep_count} dependency relationship(s) "
            f"and {entity_count} entity node(s) in the impact graph. "
            "The primary failure vector is traced through direct structural dependencies."
        )
        if dep_count == 0:
            answer = (
                "No direct structural dependencies were found for the query subject. "
                "Root cause could not be determined from graph structure alone."
            )

        return _make_result(
            context,
            answer=answer,
            hypothesis_statement=(
                f"Root cause is in the dependency chain affecting {dep_count} relationship(s)."
            ),
            supporting_ids=context.source_ids(),
        )


class BlastRadiusStrategy:
    """Answers 'What breaks if X changes or fails?' questions."""

    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.BLAST_RADIUS

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="blast_radius_strategy",
            description="BlastRadiusStrategy: computing transitive impact set.",
            inputs=context.source_ids(),
        )

        impacted_entities = [
            e.get("name", e.get("id", "unknown"))
            for e in context.entities[:10]
        ]
        impacted_caps = [
            c.get("name", c.get("id", "unknown"))
            for c in context.capabilities[:5]
        ]

        total = len(context.entities) + len(context.capabilities)
        if total == 0:
            answer = (
                "Blast radius is empty — no entities or capabilities are directly "
                "reachable from the query subject in the current graph snapshot."
            )
        else:
            answer = (
                f"Blast radius spans {len(context.entities)} entity/entities and "
                f"{len(context.capabilities)} capability/capabilities. "
            )
            if impacted_entities:
                answer += f"Affected entities include: {', '.join(impacted_entities[:5])}."
            if impacted_caps:
                answer += f" Affected capabilities include: {', '.join(impacted_caps[:5])}."

        lims = _detect_limitations(context)
        lims.append(ReasoningLimitation(
            reason="Cross-repository blast radius not computed in Phase 7A.",
            affected_area="blast_radius",
            impact="Services in external repositories are not counted in the impact set.",
        ))

        return ReasoningResult(
            execution_id=context.execution_id,
            question=context.query,
            answer=answer,
            confidence=ReasoningConfidence.compute(
                weights=EvidenceWeightRegistry.all_weights(),
                found_types=context.all_collected_source_types(),
                rationale=f"Impact graph contains {total} nodes.",
            ),
            reasoning_chain=context.chain,
            provenance_graph=_build_provenance(context, answer),
            evidence=list(context.validated_evidence),
            selected_hypothesis=ReasoningHypothesis(
                hypothesis_id=str(uuid.uuid4()),
                statement=f"Blast radius spans {total} nodes.",
                supporting_ids=context.source_ids(),
                score=min(1.0, total / 100.0) if total > 0 else 0.0,
                is_selected=True,
            ),
            limitations=lims,
            generated_at=datetime.utcnow(),
            source_ids=context.source_ids(),
            snapshot=context.snapshot,
        )


class CounterfactualStrategy:
    """Answers 'What would happen if we changed X?' questions."""

    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.COUNTERFACTUAL

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="counterfactual_strategy",
            description="CounterfactualStrategy: simulating hypothetical graph mutations.",
            inputs=context.source_ids(),
        )

        answer = (
            f"Counterfactual analysis of '{context.query}': "
            f"Removing or changing the subject would affect {len(context.relationships)} "
            f"direct relationship(s) and propagate to {len(context.entities)} downstream node(s). "
            "Full causal simulation requires Phase 7C causal reasoning engine."
        )

        return _make_result(
            context,
            answer=answer,
            hypothesis_statement=(
                f"Hypothetical change propagates through {len(context.relationships)} relationship(s)."
            ),
            supporting_ids=context.source_ids(),
        )


class ArchitectureStrategy:
    """Answers 'What are the architectural patterns / boundaries?' questions."""

    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type in (
            ReasoningQuestionType.ARCHITECTURE,
            ReasoningQuestionType.DEPENDENCY,
        )

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="architecture_strategy",
            description="ArchitectureStrategy: analysing structural patterns and boundaries.",
            inputs=context.source_ids(),
        )

        cap_count = len(context.capabilities)
        entity_count = len(context.entities)
        rel_count = len(context.relationships)

        answer = (
            f"Architecture analysis: {cap_count} capability boundary/boundaries identified, "
            f"{entity_count} structural entity/entities, "
            f"{rel_count} structural relationship(s)."
        )
        if context.concepts:
            concept_names = [c.get("name", "?") for c in context.concepts[:3]]
            answer += f" Key concepts: {', '.join(concept_names)}."

        return _make_result(
            context,
            answer=answer,
            hypothesis_statement=(
                f"Architecture contains {cap_count} capabilities across {entity_count} entities."
            ),
            supporting_ids=context.source_ids(),
        )


class GeneralStrategy:
    """Catch-all strategy for unclassified or GENERAL question types."""

    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.GENERAL

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="general_strategy",
            description="GeneralStrategy: applying generic evidence aggregation.",
            inputs=context.source_ids(),
        )

        ev_count = len(context.validated_evidence)
        answer = (
            f"General reasoning over {ev_count} validated evidence node(s). "
            "No specific question type was detected — presenting aggregate graph intelligence."
        )

        return _make_result(
            context,
            answer=answer,
            hypothesis_statement=f"General summary across {ev_count} evidence node(s).",
            supporting_ids=context.source_ids(),
        )


# ── Registry ──────────────────────────────────────────────────────────────────

class ReasoningStrategyRegistry:
    """Registry that maps question types to concrete strategy instances.

    Usage::

        registry = ReasoningStrategyRegistry.default()
        strategy = registry.resolve(ReasoningQuestionType.WHY)
        result   = strategy.execute(context)

    Extending for Phase 7B/7C::

        registry.register(DriftStrategy())
        registry.register(OwnershipStrategy())
    """

    def __init__(self) -> None:
        self._strategies: list[IReasoningStrategy] = []

    def register(self, strategy: IReasoningStrategy) -> None:
        """Register a new strategy.  Later registrations have higher priority."""
        self._strategies.append(strategy)

    def resolve(self, question_type: ReasoningQuestionType) -> IReasoningStrategy:
        """Return the first registered strategy that supports *question_type*.

        Falls back to ``GeneralStrategy`` if no specific match is found.

        Raises:
            RuntimeError: If no strategy is registered at all (should never
                          happen after ``default()`` is used).
        """
        # Iterate in reverse so later registrations (Phase 7B/7C) win.
        for strategy in reversed(self._strategies):
            if strategy.supports(question_type):
                return strategy
        # Ultimate fallback — always succeeds when default() was called.
        for strategy in reversed(self._strategies):
            if strategy.supports(ReasoningQuestionType.GENERAL):
                return strategy
        raise RuntimeError(
            f"No strategy registered for question_type={question_type!r} "
            "and no GeneralStrategy fallback found."
        )

    def registered_types(self) -> list[ReasoningQuestionType]:
        """Return all question types that have at least one supporting strategy."""
        supported: list[ReasoningQuestionType] = []
        for qt in ReasoningQuestionType:
            for strategy in self._strategies:
                if strategy.supports(qt):
                    supported.append(qt)
                    break
        return supported

    @classmethod
    def default(cls) -> "ReasoningStrategyRegistry":
        """Build and return the default Phase 7A registry with all strategies."""
        registry = cls()
        # Register in ascending priority order (GeneralStrategy is the lowest)
        registry.register(GeneralStrategy())
        registry.register(ArchitectureStrategy())
        registry.register(CounterfactualStrategy())
        registry.register(BlastRadiusStrategy())
        registry.register(RootCauseStrategy())
        registry.register(WhyStrategy())
        return registry
