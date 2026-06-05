"""Use case for fetching detection evidence associated with a logic version."""

from typing import Callable, List
import uuid

from src.application.dtos.logic_responses import LogicEvidenceResponse
from src.application.ports.unit_of_work import IUnitOfWork


class GetLogicEvidenceUseCase:
    """Retrieves all LogicEvidence supporting a specific LogicVersion detection."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(self, logic_version_id_str: str) -> List[LogicEvidenceResponse]:
        """Fetch all evidence supporting the given LogicVersion UUID."""
        version_id = uuid.UUID(logic_version_id_str)
        with self.uow_factory() as uow:
            evidence = uow.logic_evidence.get_by_logic_version(version_id)

            return [
                LogicEvidenceResponse(
                    id=str(e.id),
                    logic_version_id=str(e.logic_version_id),
                    evidence_type=e.evidence_type.value,
                    file_path=e.file_path,
                    start_line=e.start_line,
                    end_line=e.end_line,
                    ast_node_type=e.ast_node_type,
                    matched_symbol=e.matched_symbol,
                    matched_rule_id=e.matched_rule_id,
                    call_chain=e.call_chain,
                    data_flow_path=e.data_flow_path,
                    confidence_contribution=e.confidence_contribution,
                    metadata=e.metadata,
                    detected_at=e.detected_at,
                )
                for e in evidence
            ]
