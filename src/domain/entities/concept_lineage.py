"""Domain entity representing genealogical parent/child relationships between concepts."""

import uuid
from dataclasses import dataclass
from typing import Optional


@dataclass
class ConceptLineage:
    """Tracks taxonomy evolution and parenting of concepts across commits."""

    id: uuid.UUID
    concept_id: uuid.UUID
    parent_concept_id: Optional[uuid.UUID]
    relation_type: str  # e.g., PARENT, DERIVED_FROM, MERGED_INTO
    valid_from_commit: str
    valid_to_commit: Optional[str] = None

    def validate(self) -> None:
        """Validates invariants of the ConceptLineage."""
        if not self.concept_id:
            raise ValueError("ConceptLineage.concept_id must be specified.")
        if not self.relation_type or not self.relation_type.strip():
            raise ValueError("ConceptLineage.relation_type must be specified.")
        if not self.valid_from_commit or not self.valid_from_commit.strip():
            raise ValueError("ConceptLineage.valid_from_commit must be specified.")
