"""Domain entity representing a single piece of evidence supporting a logic detection."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.domain.enums.evidence_type import EvidenceType
from src.domain.exceptions import InvalidEntityException


@dataclass
class LogicEvidence:
    """
    A LogicEvidence record stores one atomic piece of information that contributed
    to the detection of a LogicVersion.

    Evidence items are collected during AST analysis, data-flow tracing, or
    pattern-rule evaluation.  Together they form an auditable justification trail
    for every detection confidence score.
    """

    id: uuid.UUID
    """Unique identifier for this evidence record."""

    logic_version_id: uuid.UUID
    """Reference to the LogicVersion this evidence supports."""

    evidence_type: EvidenceType
    """Category of evidence (AST_CALL, DATA_FLOW, etc.)."""

    file_path: str
    """Absolute or repository-relative path of the source file."""

    start_line: int
    """Starting line number (1-indexed) of the matching AST node or code span."""

    end_line: int
    """Ending line number (1-indexed) of the matching AST node or code span."""

    ast_node_type: str | None = None
    """The AST node type as returned by the parser (e.g., 'Call', 'Import')."""

    matched_symbol: str | None = None
    """The fully-qualified symbol that was matched (e.g., 'bcrypt.checkpw')."""

    matched_rule_id: str | None = None
    """ID of the pattern rule that produced this evidence, if any."""

    call_chain: list[str] = field(default_factory=list)
    """Ordered list of call frames leading to the matched symbol (for call-chain evidence)."""

    data_flow_path: list[str] | None = None
    """Ordered list of data-flow nodes from source to sink (required for DATA_FLOW evidence)."""

    confidence_contribution: float = 0.0
    """The fractional confidence contribution of this single evidence item."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Arbitrary extensible metadata."""

    detected_at: datetime = field(default_factory=datetime.utcnow)
    """UTC timestamp when this evidence was recorded."""

    def validate(self) -> None:
        """
        Validate domain invariants for this LogicEvidence record.

        Rules enforced:
            - AST_CALL evidence must have a non-None matched_symbol.
            - DATA_FLOW evidence must have a data_flow_path with at least 2 nodes.

        Raises:
            InvalidEntityException: When a validation rule is violated.
        """
        if self.evidence_type == EvidenceType.AST_CALL and self.matched_symbol is None:
            raise InvalidEntityException(
                f"LogicEvidence of type AST_CALL must have matched_symbol set "
                f"(id={self.id}, logic_version_id={self.logic_version_id})"
            )
        if self.evidence_type == EvidenceType.DATA_FLOW:
            if self.data_flow_path is None or len(self.data_flow_path) < 2:
                raise InvalidEntityException(
                    f"LogicEvidence of type DATA_FLOW must have data_flow_path "
                    f"with at least 2 nodes (id={self.id}, "
                    f"logic_version_id={self.logic_version_id})"
                )
