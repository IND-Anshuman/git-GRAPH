"""
Phase 7A — HypothesisGenerationEngine

Produces a set of competing candidate explanations (``ReasoningHypothesis``
objects) from the validated evidence in ``ReasoningContext``.

Generation strategy (Phase 7A — deterministic)
-----------------------------------------------
For each main evidence category present in validated evidence, the engine
generates one hypothesis asserting the category's contribution to the answer.

Example for a WHY question:
  Evidence types: {capability, entity, concept}
  Generated hypotheses:
    H1: "Subject exists because of capability evidence: ..."
    H2: "Subject exists because of entity-level implementation: ..."
    H3: "Subject exists because of concept alignment: ..."

These competing hypotheses are then handed to the ``HypothesisScoringEngine``
which scores and selects the best one.

Phase 7B/7C can swap this engine for a more sophisticated generator that
uses ontology inference or causal DAG patterns.
"""

from __future__ import annotations

import uuid
import logging

from src.application.reasoning.reasoning_context import ReasoningContext
from src.application.reasoning.reasoning_hypothesis import ReasoningHypothesis
from src.application.reasoning.evidence_weight_registry import EvidenceWeightRegistry
from src.application.reasoning.reasoning_question_type import ReasoningQuestionType

logger = logging.getLogger(__name__)

# Maps question type to hypothesis templates
_TEMPLATES: dict[ReasoningQuestionType, list[str]] = {
    ReasoningQuestionType.WHY: [
        "The subject exists to support capability: {capability_list}.",
        "The subject implements domain concept(s): {concept_list}.",
        "The subject is a structural entity fulfilling: {entity_list}.",
    ],
    ReasoningQuestionType.ROOT_CAUSE: [
        "Root cause is in the structural dependency chain: {relationship_list}.",
        "Root cause originates from capability failure: {capability_list}.",
        "Root cause is a missing or broken entity: {entity_list}.",
    ],
    ReasoningQuestionType.BLAST_RADIUS: [
        "Direct blast radius includes entities: {entity_list}.",
        "Capability impact spans: {capability_list}.",
        "Transitive relationship exposure: {relationship_list}.",
    ],
    ReasoningQuestionType.COUNTERFACTUAL: [
        "Hypothetical change propagates through relationships: {relationship_list}.",
        "Removing the subject breaks capabilities: {capability_list}.",
        "Alternative path: {entity_list}.",
    ],
    ReasoningQuestionType.ARCHITECTURE: [
        "Architecture is defined by capability boundaries: {capability_list}.",
        "Structural entities form the core: {entity_list}.",
        "Concepts encode the design vocabulary: {concept_list}.",
    ],
}
_DEFAULT_TEMPLATES = [
    "Primary evidence is from {source_type}: {items}.",
    "Secondary evidence supports the answer via {source_type}: {items}.",
]


def _names(ev_list, source_type: str, limit: int = 5) -> str:
    items = [ev.description[:60] for ev in ev_list if ev.source_type == source_type]
    return ", ".join(items[:limit]) or "N/A"


class HypothesisGenerationEngine:
    """Generates competing candidate hypotheses from validated evidence.

    All hypotheses produced here are unscored (score=0.0).  The
    ``HypothesisScoringEngine`` assigns scores in the next pipeline stage.
    """

    def generate(self, context: ReasoningContext) -> None:
        """Populate ``context.hypotheses`` with candidate explanations.

        Args:
            context: Mutable pipeline carry-bag (modified in-place).
        """
        context.chain.add_step(
            step_type="hypothesis_generation",
            description=(
                f"Generating hypotheses from {len(context.validated_evidence)} "
                f"validated evidence nodes, question_type={context.question_type.value}."
            ),
            inputs=list(context.all_collected_source_types()),
        )

        evidence_by_type: dict[str, list] = {}
        for ev in context.validated_evidence:
            evidence_by_type.setdefault(ev.source_type, []).append(ev)

        templates = _TEMPLATES.get(context.question_type)
        hypotheses: list[ReasoningHypothesis] = []

        if templates:
            cap_list = _names(context.validated_evidence, "capability")
            concept_list = _names(context.validated_evidence, "concept")
            entity_list = _names(context.validated_evidence, "entity")
            rel_list = _names(context.validated_evidence, "relationship")

            for tmpl in templates:
                statement = tmpl.format(
                    capability_list=cap_list,
                    concept_list=concept_list,
                    entity_list=entity_list,
                    relationship_list=rel_list,
                )
                hypotheses.append(ReasoningHypothesis(
                    hypothesis_id=str(uuid.uuid4()),
                    statement=statement,
                    supporting_ids=[
                        ev.source_id for ev in context.validated_evidence
                    ],
                ))
        else:
            # Fallback: one hypothesis per evidence type
            for source_type, evs in evidence_by_type.items():
                items = ", ".join(ev.description[:60] for ev in evs[:5])
                statement = f"Evidence from {source_type}: {items}."
                hypotheses.append(ReasoningHypothesis(
                    hypothesis_id=str(uuid.uuid4()),
                    statement=statement,
                    supporting_ids=[ev.source_id for ev in evs],
                ))

        context.hypotheses = hypotheses

        context.chain.add_step(
            step_type="hypothesis_generation_complete",
            description=f"Generated {len(hypotheses)} hypothesis/hypotheses.",
            outputs=[h.hypothesis_id for h in hypotheses],
        )
