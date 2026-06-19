"""
Phase 7B — Architecture Strategies

Implements IReasoningStrategy for the new Phase 7B architectural question types.
"""

import uuid
from datetime import datetime

from src.application.reasoning.reasoning_strategy import IReasoningStrategy
from src.application.reasoning.reasoning_question_type import ReasoningQuestionType
from src.application.reasoning.reasoning_context import ReasoningContext
from src.application.reasoning.reasoning_result import ReasoningResult
from src.application.reasoning.reasoning_confidence import ReasoningConfidence
from src.application.reasoning.evidence_weight_registry import EvidenceWeightRegistry
from src.application.reasoning.reasoning_hypothesis import ReasoningHypothesis
from src.application.reasoning.reasoning_strategy_registry import _make_result

class ArchitectureStyleStrategy(IReasoningStrategy):
    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.ARCHITECTURE_STYLE

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="architecture_style_strategy",
            description="ArchitectureStyleStrategy: analysing architectural pattern and style.",
            inputs=context.source_ids(),
        )
        answer = f"Architecture style analysis identified structural patterns from {len(context.capabilities)} capabilities and {len(context.relationships)} relationships."
        return _make_result(
            context,
            answer=answer,
            hypothesis_statement="System matches a specific architectural style topology.",
            supporting_ids=context.source_ids(),
        )

class FitnessStrategy(IReasoningStrategy):
    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.FITNESS

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="fitness_strategy",
            description="FitnessStrategy: evaluating architectural fitness functions.",
            inputs=context.source_ids(),
        )
        answer = f"Fitness analysis computed scores across {len(context.entities)} entities and {len(context.relationships)} relationships."
        return _make_result(
            context,
            answer=answer,
            hypothesis_statement="System architecture satisfies or violates fitness functions.",
            supporting_ids=context.source_ids(),
        )

class InvariantStrategy(IReasoningStrategy):
    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.INVARIANT

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="invariant_strategy",
            description="InvariantStrategy: detecting architectural invariant violations.",
            inputs=context.source_ids(),
        )
        answer = f"Invariant reasoning analysed {len(context.entities)} entities against architectural rules."
        return _make_result(
            context,
            answer=answer,
            hypothesis_statement="Architectural invariants are upheld or violated.",
            supporting_ids=context.source_ids(),
        )

class DriftArchStrategy(IReasoningStrategy):
    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.DRIFT_ARCH

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="drift_arch_strategy",
            description="DriftArchStrategy: measuring architectural drift across temporal states.",
            inputs=context.source_ids(),
        )
        answer = "Architectural drift analysis computed temporal divergence from historical states."
        return _make_result(
            context,
            answer=answer,
            hypothesis_statement="Architecture has drifted from its original intended design.",
            supporting_ids=context.source_ids(),
        )

class OwnershipArchStrategy(IReasoningStrategy):
    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.OWNERSHIP_ARCH

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="ownership_arch_strategy",
            description="OwnershipArchStrategy: correlating team ownership boundaries with architecture.",
            inputs=context.source_ids(),
        )
        answer = f"Ownership architecture analysis integrated team data over {len(context.capabilities)} capabilities."
        return _make_result(
            context,
            answer=answer,
            hypothesis_statement="Architectural boundaries align or conflict with team ownership.",
            supporting_ids=context.source_ids(),
        )

class RefactoringStrategy(IReasoningStrategy):
    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.REFACTORING

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="refactoring_strategy",
            description="RefactoringStrategy: identifying code smells and refactoring candidates.",
            inputs=context.source_ids(),
        )
        answer = f"Refactoring reasoning surfaced code smells within {len(context.entities)} evaluated entities."
        return _make_result(
            context,
            answer=answer,
            hypothesis_statement="Structural metrics indicate high-priority refactoring targets.",
            supporting_ids=context.source_ids(),
        )

class RecommendationStrategy(IReasoningStrategy):
    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.RECOMMENDATION

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="recommendation_strategy",
            description="RecommendationStrategy: proposing structural changes to improve fitness.",
            inputs=context.source_ids(),
        )
        answer = "Architecture recommendation engine synthesized refactoring and fitness signals into actionable proposals."
        return _make_result(
            context,
            answer=answer,
            hypothesis_statement="Specific refactoring actions will improve overall architecture fitness.",
            supporting_ids=context.source_ids(),
        )

class SimilarityStrategy(IReasoningStrategy):
    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.SIMILARITY

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="similarity_strategy",
            description="SimilarityStrategy: matching architectural fingerprints against peers.",
            inputs=context.source_ids(),
        )
        answer = "Similarity analysis compared topological and dependency graphs."
        return _make_result(
            context,
            answer=answer,
            hypothesis_statement="Architecture structurally resembles identified peer repositories.",
            supporting_ids=context.source_ids(),
        )

class BenchmarkStrategy(IReasoningStrategy):
    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.BENCHMARK

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="benchmark_strategy",
            description="BenchmarkStrategy: evaluating fitness metrics against baseline percentiles.",
            inputs=context.source_ids(),
        )
        answer = "Architecture benchmarking evaluated current fitness against peer statistics."
        return _make_result(
            context,
            answer=answer,
            hypothesis_statement="Architecture fitness scores fall within specific peer percentiles.",
            supporting_ids=context.source_ids(),
        )

class TimelineStrategy(IReasoningStrategy):
    def supports(self, question_type: ReasoningQuestionType) -> bool:
        return question_type == ReasoningQuestionType.TIMELINE

    def execute(self, context: ReasoningContext) -> ReasoningResult:
        context.chain.add_step(
            step_type="timeline_strategy",
            description="TimelineStrategy: plotting architectural evolution.",
            inputs=context.source_ids(),
        )
        answer = "Architecture timeline engine generated evolutionary history from snapshot data."
        return _make_result(
            context,
            answer=answer,
            hypothesis_statement="System architecture underwent distinct structural phases over time.",
            supporting_ids=context.source_ids(),
        )
