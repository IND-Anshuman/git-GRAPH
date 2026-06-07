"""Domain entity representing a semantic dependency/link between concepts at a commit."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from src.domain.enums.concept_relationship_type import ConceptRelationshipType
from src.domain.exceptions import InvalidEntityException
from src.domain.value_objects.repository_id import RepositoryId


@dataclass
class ConceptRelationship:
    """
    ConceptRelationship captures semantic and structural edges (e.g. DEPENDS_ON)
    linking ConceptNodes at a specific Git commit.
    """

    id: uuid.UUID
    """Unique identifier for this concept relationship link."""

    repository_id: RepositoryId
    """The repository containing this relationship."""

    commit_hash: str
    """The Git commit hash this relationship is verified at."""

    from_concept_id: uuid.UUID
    """The source concept node ID."""

    to_concept_id: uuid.UUID
    """The destination concept node ID."""

    relationship_type: ConceptRelationshipType
    """The type of semantic linkage (e.g. DEPENDS_ON)."""

    confidence: float
    """Confidence score of this relationship inference [0.00, 1.00]."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Dynamic coupling properties."""

    created_at: datetime = field(default_factory=datetime.utcnow)
    """Timestamp when this relationship edge was generated."""

    def validate(self) -> None:
        """
        Validate ConceptRelationship invariants.

        Raises:
            InvalidEntityException: If out of bounds or cycles exist.
        """
        if self.from_concept_id == self.to_concept_id:
            raise InvalidEntityException("A concept relationship cannot link a concept node to itself.")
        if not (0.00 <= self.confidence <= 1.00):
            raise InvalidEntityException("relationship confidence must be in [0.00, 1.00].")
        if not self.commit_hash or len(self.commit_hash) != 40:
            raise InvalidEntityException("commit_hash must be a valid 40-character sha.")
