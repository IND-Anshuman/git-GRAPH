"""Domain entity representing a structured breakdown explanation for a concept version."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from src.domain.exceptions import InvalidEntityException


@dataclass
class ConceptExplanation:
    """
    ConceptExplanation holds audit-verifiable explanations showing why
    a concept was detected and what AST footprints exist.
    """

    id: uuid.UUID
    """Unique identifier of this explanation."""

    concept_version_id: uuid.UUID
    """The associated ConceptVersion ID."""

    summary: str
    """Deterministic summary text explaining detection triggers and confidence."""

    detail: Dict[str, Any] = field(default_factory=dict)
    """JSON map containing primary triggers and structural footprint sizes."""

    created_at: datetime = field(default_factory=datetime.utcnow)
    """Timestamp when this explanation was generated."""

    def validate(self) -> None:
        """
        Validate ConceptExplanation invariants.

        Raises:
            InvalidEntityException: If summary is empty.
        """
        if not self.summary or not self.summary.strip():
            raise InvalidEntityException("ConceptExplanation summary must not be empty.")
