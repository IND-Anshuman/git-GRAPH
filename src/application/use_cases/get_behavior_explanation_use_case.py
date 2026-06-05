"""Use case for fetching the rule explanation verdict for a logic version."""

from typing import Callable, Optional
import uuid

from src.application.dtos.logic_responses import (
    BehaviorExplanationResponse,
    ConfidenceBreakdownResponse,
    RuleVerdictResponse,
)
from src.application.ports.unit_of_work import IUnitOfWork


class GetBehaviorExplanationUseCase:
    """Retrieves the BehaviorExplanation and per-rule verdicts for a logic version."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(
        self, logic_version_id_str: str
    ) -> Optional[BehaviorExplanationResponse]:
        """Fetch the explanation associated with the given LogicVersion UUID."""
        version_id = uuid.UUID(logic_version_id_str)
        with self.uow_factory() as uow:
            exp = uow.behavior_explanations.get_by_logic_version(version_id)
            if not exp:
                return None

            verdicts = [
                RuleVerdictResponse(
                    rule_id=v.rule_id,
                    rule_description=v.rule_description,
                    passed=v.passed,
                    contribution=v.contribution,
                    evidence_ref=str(v.evidence_ref) if v.evidence_ref else None,
                )
                for v in exp.rule_verdicts
            ]

            return BehaviorExplanationResponse(
                id=str(exp.id),
                logic_version_id=str(exp.logic_version_id),
                behavior_name=exp.behavior_name,
                ontology_path=exp.ontology_path,
                overall_confidence=exp.overall_confidence,
                confidence_breakdown=ConfidenceBreakdownResponse(
                    overall_confidence=exp.confidence_breakdown.overall_confidence,
                    ast_confidence=exp.confidence_breakdown.ast_confidence,
                    dependency_confidence=exp.confidence_breakdown.dependency_confidence,
                    data_flow_confidence=exp.confidence_breakdown.data_flow_confidence,
                    pattern_confidence=exp.confidence_breakdown.pattern_confidence,
                    structural_confidence=exp.confidence_breakdown.structural_confidence,
                    evidence_count=exp.confidence_breakdown.evidence_count,
                ),
                matched_pattern_ids=exp.matched_pattern_ids,
                evidence_summary=exp.evidence_summary,
                rule_verdicts=verdicts,
                is_stale=exp.is_stale,
                generated_at=exp.generated_at,
                metadata=exp.metadata,
            )
