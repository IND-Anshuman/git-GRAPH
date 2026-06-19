"""
Phase 7A — QueryPlanner

Classifies the user's natural-language question into a ``ReasoningQuestionType``
and decides which evidence collection scopes the ``EvidenceCollectionEngine``
should activate.

Design
------
The planner uses keyword matching against the lowercased query text.
This is intentionally simple and deterministic — no ML or embeddings.

Phase 7C will extend this with intent-aware classification that queries
the ``IntentNode`` layer, but Phase 7A must stay purely deterministic.

Query plan
----------
A ``QueryPlan`` carries:
  * ``question_type``   — classified type (used by strategy registry).
  * ``collect_scopes``  — list of evidence collection scope names.
  * ``target_term``     — extracted subject of the question (best-effort).
  * ``max_hops``        — how many relationship hops to traverse.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.application.reasoning.reasoning_question_type import ReasoningQuestionType


@dataclass
class QueryPlan:
    """The output of the QueryPlanner — controls downstream collection."""

    question_type: ReasoningQuestionType
    """Classified question type."""

    collect_scopes: list[str]
    """Which evidence collection scopes to activate.
    Valid values: "entities", "relationships", "concepts",
    "capabilities", "flows", "artifacts", "ownership", "timeline".
    """

    target_term: str
    """Best-effort extraction of the query subject (e.g. 'CheckoutService')."""

    max_hops: int = 2
    """How many relationship hops the expansion engine should walk."""

    metadata: dict = field(default_factory=dict)


# ── Keyword lookup tables ──────────────────────────────────────────────────────

_WHY_KEYWORDS = {"why", "purpose", "reason", "exist", "designed", "intent"}
_ROOT_CAUSE_KEYWORDS = {"root cause", "caused by", "reason for", "incident", "failure", "bug"}
_BLAST_RADIUS_KEYWORDS = {"blast radius", "impact", "affects", "depends on", "what breaks", "downstream"}
_COUNTERFACTUAL_KEYWORDS = {"what if", "would happen", "if we", "hypothetically", "change", "remove"}
_ARCHITECTURE_KEYWORDS = {"architecture", "pattern", "boundary", "structure", "design", "layer"}
_DEPENDENCY_KEYWORDS = {"depends on", "depend on", "dependency", "dependencies", "require", "imports"}
_DRIFT_KEYWORDS = {"drift", "changed", "diverged", "originally", "intended design"}
_EVOLUTION_KEYWORDS = {"evolved", "history", "timeline", "over time", "when was", "how did"}
_OWNERSHIP_KEYWORDS = {"owner", "owns", "responsible", "team", "codeowners", "who"}
_COUNTERFACTUAL_KEYWORDS2 = {"counterfactual", "simulate"}
_DECISION_KEYWORDS = {"why was", "decision", "adr", "decided", "trade-off", "chose"}
_INTENT_KEYWORDS = {"business goal", "objective", "success metric", "kpi", "purpose of"}

_ARCHITECTURE_STYLE_KEYWORDS = {"architectural style", "clean architecture", "hexagonal", "layered", "microservice", "cqrs", "modular monolith"}
_FITNESS_KEYWORDS = {"fitness", "cohesion", "coupling", "distance from main sequence", "cyclicity", "instability"}
_INVARIANT_KEYWORDS = {"invariant", "violation", "rule", "forbidden target", "must not"}
_DRIFT_ARCH_KEYWORDS = {"architectural drift", "structural drift", "dependency drift"}
_OWNERSHIP_ARCH_KEYWORDS = {"knowledge silo", "bus factor", "team ownership", "overloaded team"}
_REFACTORING_KEYWORDS = {"refactor", "code smell", "god class", "shotgun surgery", "blob", "feature envy"}
_RECOMMENDATION_KEYWORDS = {"recommend", "improve architecture", "split service", "merge"}
_SIMILARITY_KEYWORDS = {"similar to", "comparable", "like", "similarity"}
_BENCHMARK_KEYWORDS = {"benchmark", "compare with peers", "percentile"}
_TIMELINE_KEYWORDS = {"architectural timeline", "evolution of architecture"}


def _score_question_type(query_lower: str) -> ReasoningQuestionType:
    """Return the best matching question type for the lowercased query."""
    # Multi-word phrases first (higher specificity)
    if any(kw in query_lower for kw in _ROOT_CAUSE_KEYWORDS):
        return ReasoningQuestionType.ROOT_CAUSE
    if any(kw in query_lower for kw in _BLAST_RADIUS_KEYWORDS):
        return ReasoningQuestionType.BLAST_RADIUS
    if any(kw in query_lower for kw in _COUNTERFACTUAL_KEYWORDS) or any(
        kw in query_lower for kw in _COUNTERFACTUAL_KEYWORDS2
    ):
        return ReasoningQuestionType.COUNTERFACTUAL
    if any(kw in query_lower for kw in _DECISION_KEYWORDS):
        return ReasoningQuestionType.DECISION
    if any(kw in query_lower for kw in _INTENT_KEYWORDS):
        return ReasoningQuestionType.INTENT
    if any(kw in query_lower for kw in _DRIFT_KEYWORDS):
        return ReasoningQuestionType.DRIFT
    if any(kw in query_lower for kw in _EVOLUTION_KEYWORDS):
        return ReasoningQuestionType.EVOLUTION
    if any(kw in query_lower for kw in _OWNERSHIP_KEYWORDS):
        return ReasoningQuestionType.OWNERSHIP
    if any(kw in query_lower for kw in _DEPENDENCY_KEYWORDS):
        return ReasoningQuestionType.DEPENDENCY
    if any(kw in query_lower for kw in _ARCHITECTURE_KEYWORDS):
        return ReasoningQuestionType.ARCHITECTURE
    if any(kw in query_lower for kw in _ARCHITECTURE_STYLE_KEYWORDS):
        return ReasoningQuestionType.ARCHITECTURE_STYLE
    if any(kw in query_lower for kw in _FITNESS_KEYWORDS):
        return ReasoningQuestionType.FITNESS
    if any(kw in query_lower for kw in _INVARIANT_KEYWORDS):
        return ReasoningQuestionType.INVARIANT
    if any(kw in query_lower for kw in _DRIFT_ARCH_KEYWORDS):
        return ReasoningQuestionType.DRIFT_ARCH
    if any(kw in query_lower for kw in _OWNERSHIP_ARCH_KEYWORDS):
        return ReasoningQuestionType.OWNERSHIP_ARCH
    if any(kw in query_lower for kw in _REFACTORING_KEYWORDS):
        return ReasoningQuestionType.REFACTORING
    if any(kw in query_lower for kw in _RECOMMENDATION_KEYWORDS):
        return ReasoningQuestionType.RECOMMENDATION
    if any(kw in query_lower for kw in _SIMILARITY_KEYWORDS):
        return ReasoningQuestionType.SIMILARITY
    if any(kw in query_lower for kw in _BENCHMARK_KEYWORDS):
        return ReasoningQuestionType.BENCHMARK
    if any(kw in query_lower for kw in _TIMELINE_KEYWORDS):
        return ReasoningQuestionType.TIMELINE
    if any(kw in query_lower for kw in _WHY_KEYWORDS):
        return ReasoningQuestionType.WHY
    return ReasoningQuestionType.GENERAL

_SCOPE_MAP: dict[ReasoningQuestionType, list[str]] = {
    ReasoningQuestionType.WHY: ["entities", "capabilities", "concepts", "relationships"],
    ReasoningQuestionType.ROOT_CAUSE: ["entities", "relationships", "flows", "artifacts"],
    ReasoningQuestionType.BLAST_RADIUS: ["entities", "relationships", "capabilities", "flows"],
    ReasoningQuestionType.COUNTERFACTUAL: ["entities", "relationships", "capabilities"],
    ReasoningQuestionType.ARCHITECTURE: ["entities", "relationships", "capabilities", "concepts"],
    ReasoningQuestionType.DEPENDENCY: ["entities", "relationships"],
    ReasoningQuestionType.DRIFT: ["entities", "capabilities", "artifacts", "timeline"],
    ReasoningQuestionType.EVOLUTION: ["entities", "artifacts", "timeline"],
    ReasoningQuestionType.OWNERSHIP: ["entities", "ownership"],
    ReasoningQuestionType.DECISION: ["entities", "artifacts", "concepts"],
    ReasoningQuestionType.INTENT: ["entities", "capabilities", "concepts"],
    ReasoningQuestionType.CAUSAL: ["entities", "relationships", "flows", "capabilities"],
    ReasoningQuestionType.RISK: ["entities", "capabilities", "relationships"],
    ReasoningQuestionType.ARCHITECTURE_STYLE: ["entities", "relationships", "capabilities"],
    ReasoningQuestionType.FITNESS: ["entities", "relationships", "capabilities"],
    ReasoningQuestionType.INVARIANT: ["entities", "relationships", "capabilities"],
    ReasoningQuestionType.DRIFT_ARCH: ["entities", "relationships", "capabilities", "artifacts"],
    ReasoningQuestionType.OWNERSHIP_ARCH: ["entities", "capabilities", "ownership"],
    ReasoningQuestionType.REFACTORING: ["entities", "relationships", "capabilities"],
    ReasoningQuestionType.RECOMMENDATION: ["entities", "relationships", "capabilities"],
    ReasoningQuestionType.SIMILARITY: ["entities", "relationships", "capabilities", "flows"],
    ReasoningQuestionType.BENCHMARK: ["entities", "relationships", "capabilities"],
    ReasoningQuestionType.TIMELINE: ["entities", "relationships", "timeline", "artifacts"],
    ReasoningQuestionType.GENERAL: ["entities", "relationships", "concepts", "capabilities"],
}

_HOP_MAP: dict[ReasoningQuestionType, int] = {
    ReasoningQuestionType.BLAST_RADIUS: 3,
    ReasoningQuestionType.ROOT_CAUSE: 3,
    ReasoningQuestionType.DEPENDENCY: 2,
    ReasoningQuestionType.ARCHITECTURE: 2,
    ReasoningQuestionType.COUNTERFACTUAL: 2,
    ReasoningQuestionType.ARCHITECTURE_STYLE: 3,
    ReasoningQuestionType.SIMILARITY: 3,
}


def _extract_target_term(query: str) -> str:
    """Naively extract the first capitalised word as the target term."""
    for word in query.split():
        cleaned = word.strip("?.,!\"'")
        if cleaned and cleaned[0].isupper() and len(cleaned) > 2:
            return cleaned
    return query.split()[0] if query.split() else ""


class QueryPlanner:
    """Classifies a natural-language question and produces a :class:`QueryPlan`.

    The planner is intentionally stateless — each call to ``plan`` is
    independent and deterministic for the same input.
    """

    def plan(self, query: str) -> QueryPlan:
        """Classify *query* and return a :class:`QueryPlan`.

        Args:
            query: Raw user question text.

        Returns:
            A :class:`QueryPlan` that controls collection and strategy routing.
        """
        if not query or not query.strip():
            raise ValueError("QueryPlanner.plan() received an empty query string.")

        query_lower = query.lower().strip()
        question_type = _score_question_type(query_lower)
        collect_scopes = _SCOPE_MAP.get(question_type, _SCOPE_MAP[ReasoningQuestionType.GENERAL])
        max_hops = _HOP_MAP.get(question_type, 2)
        target_term = _extract_target_term(query)

        return QueryPlan(
            question_type=question_type,
            collect_scopes=list(collect_scopes),
            target_term=target_term,
            max_hops=max_hops,
        )
