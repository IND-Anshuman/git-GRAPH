"""Use case for fetching the logic version history timeline of an entity."""

from typing import Callable, List

from src.application.dtos.logic_responses import (
    ConfidenceBreakdownResponse,
    LogicFingerprintResponse,
    LogicVersionResponse,
)
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.value_objects.entity_id import SEID


class GetEntityLogicHistoryUseCase:
    """Retrieves the chronological evolution timeline of logic versions for a CodeEntity."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(self, seid_str: str) -> List[LogicVersionResponse]:
        """Fetch the chronological logic version timeline of an entity by SEID."""
        entity_seid = SEID.from_string(seid_str)
        with self.uow_factory() as uow:
            versions = uow.logic_versions.list_by_entity_timeline(entity_seid)

            return [
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
