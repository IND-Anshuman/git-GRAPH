"""
Phase 7A — IReasoningStrategy (Strategy Protocol)

Defines the interface that every concrete reasoning strategy must implement.
Using a ``typing.Protocol`` gives us structural subtyping — any class that
implements ``supports`` and ``execute`` satisfies the interface without
inheriting from a base class (duck-typing friendly, but type-checker verified).

Why Strategy Pattern?
---------------------
Without this, ``ReasoningQueryEngine`` becomes a giant if/elif chain:

    if question_type == WHY:   …
    elif question_type == ROOT_CAUSE: …
    …

That chain becomes unmaintainable when Phase 7B/7C add:
  - ArchitectureStrategy, DriftStrategy, OwnershipStrategy,
    DecisionStrategy, IntentStrategy, CausalStrategy …

With the registry pattern, the orchestrator reduces to:

    strategy = registry.resolve(question_type)
    return strategy.execute(context)

Phase 7B/7C simply register new strategies without touching the engine.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.application.reasoning.reasoning_question_type import ReasoningQuestionType
from src.application.reasoning.reasoning_context import ReasoningContext
from src.application.reasoning.reasoning_result import ReasoningResult


@runtime_checkable
class IReasoningStrategy(Protocol):
    """Interface for all concrete reasoning strategies.

    Implementors
    ------------
    Phase 7A:
        WhyStrategy, RootCauseStrategy, BlastRadiusStrategy,
        CounterfactualStrategy, ArchitectureStrategy

    Phase 7B (plugged in later):
        DriftStrategy, OwnershipStrategy, RiskStrategy, EvolutionStrategy

    Phase 7C (plugged in later):
        DecisionStrategy, IntentStrategy, CausalStrategy
    """

    def supports(self, question_type: ReasoningQuestionType) -> bool:
        """Return True if this strategy can handle *question_type*.

        The registry calls this method during resolution.  A strategy MUST
        return True for exactly the question types it is designed for and
        False for all others.
        """
        ...

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        """Execute the strategy against the populated *context*.

        Pre-conditions (guaranteed by the engine before calling):
          * ``context.validated_evidence`` is populated and non-empty
            (or the strategy is responsible for handling the zero-evidence case).
          * ``context.hypotheses`` may already contain initial candidates.
          * ``context.chain`` is an open ReasoningChain ready for new steps.

        The strategy MUST:
          * Add at least one step to ``context.chain``.
          * Return a fully populated :class:`ReasoningResult`.
        """
        ...
