"""Domain entity representing a stable software capability (ConceptNode) scoped to a repository."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from src.domain.exceptions import InvalidEntityException
from src.domain.value_objects.repository_id import RepositoryId


@dataclass
class ConceptNode:
    """
    A ConceptNode represents a stable, repository-scoped software capability.
    It links AST behaviors to high-level concept boundaries.
    """

    id: uuid.UUID
    """Deterministic UUID derived from repository ID and ontology_node_id."""

    repository_id: RepositoryId
    """The repository this concept belongs to."""

    ontology_node_id: str
    """Dot-path ontology reference (e.g. 'security.authentication')."""

    name: str
    """Name of the concept."""

    description: str | None
    """Brief description of the concept's purpose."""

    is_system_defined: bool = True
    """True if defined in the core taxonomy, False if custom defined by user."""

    created_at: datetime = field(default_factory=datetime.utcnow)
    """Timestamp when this concept was first detected."""

    updated_at: datetime = field(default_factory=datetime.utcnow)
    """Timestamp when this concept was last updated."""

    def validate(self) -> None:
        """
        Validate the invariants of this ConceptNode.

        Raises:
            InvalidEntityException: If name or ontology_node_id is empty.
        """
        if not self.name or not self.name.strip():
            raise InvalidEntityException("ConceptNode name must not be empty.")
        if not self.ontology_node_id or not self.ontology_node_id.strip():
            raise InvalidEntityException("ConceptNode ontology_node_id must not be empty.")
