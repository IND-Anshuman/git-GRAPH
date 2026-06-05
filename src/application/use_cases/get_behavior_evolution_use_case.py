"""Use case for fetching the evolution history graph of a behavior signature."""

import uuid
from typing import Callable, Dict, List

from pydantic import BaseModel

from src.application.dtos.logic_responses import (
    ConfidenceBreakdownResponse,
    LogicFingerprintResponse,
    LogicTransitionResponse,
    LogicVersionResponse,
)
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.services.logic_evolution_service import (
    LogicEvolutionService,
)


class BehaviorEvolutionGraphResponse(BaseModel):
    """Payload representing versions and transitions of a behavioral logic signature."""

    versions: List[LogicVersionResponse]
    transitions: List[LogicTransitionResponse]


class GetBehaviorEvolutionUseCase:
    """Retrieves the full evolution graph (nodes = versions, edges = transitions) of a LogicSignature."""

    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        evolution_service: LogicEvolutionService,
    ) -> None:
        self.uow_factory = uow_factory
        self.evolution_service = evolution_service

    def execute(self, signature_id_str: str) -> BehaviorEvolutionGraphResponse:
        """Fetch version history and transitions for the given LogicSignature UUID."""
        sig_id = uuid.UUID(signature_id_str)
        # Use service to query versions and transitions
        versions = self.evolution_service.get_signature_history(sig_id)
        transitions = self.evolution_service.get_signature_transitions(sig_id)

        version_responses = [
            LogicVersionResponse(
                id=str(v.id),
                logic_signature_id=str(v.logic_signature_id),
                code_entity_seid=str(v.code_entity_seid),
                commit_hash=v.commit_hash,
                version_ordinal=v.version_ordinal,
                fingerprint=LogicFingerprintResponse(
                    structure_hash=v.fingerprint.structure_hash,
                    dependency_hash=v.fingerprint.dependency_hash,
                    behavioral_hash=v.fingerprint.behavioral_hash,
                    composite=v.fingerprint.composite,
                ),
                overall_confidence=v.overall_confidence,
                confidence_breakdown=ConfidenceBreakdownResponse(
                    overall_confidence=v.confidence_breakdown.overall_confidence,
                    ast_confidence=v.confidence_breakdown.ast_confidence,
                    dependency_confidence=v.confidence_breakdown.dependency_confidence,
                    data_flow_confidence=v.confidence_breakdown.data_flow_confidence,
                    pattern_confidence=v.confidence_breakdown.pattern_confidence,
                    structural_confidence=v.confidence_breakdown.structural_confidence,
                    evidence_count=v.confidence_breakdown.evidence_count,
                )
                if v.confidence_breakdown
                else None,
                is_primary=v.is_primary,
                metadata=v.metadata,
                created_at=v.created_at,
            )
            for v in versions
        ]

        transition_responses = [
            LogicTransitionResponse(
                id=str(t.id),
                from_logic_version_id=str(t.from_logic_version_id)
                if t.from_logic_version_id
                else None,
                to_logic_version_id=str(t.to_logic_version_id)
                if t.to_logic_version_id
                else None,
                transition_type=t.transition_type.value,
                similarity_score=t.similarity_score,
                overall_confidence=t.overall_confidence,
                metadata=t.metadata,
                created_at=t.created_at,
            )
            for t in transitions
        ]

        return BehaviorEvolutionGraphResponse(
            versions=version_responses, transitions=transition_responses
        )
