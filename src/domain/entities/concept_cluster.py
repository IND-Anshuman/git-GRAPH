"""Domain entity representing a high-level capability cluster grouping related concepts."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from src.domain.exceptions import InvalidEntityException


@dataclass
class ConceptCluster:
    """
    ConceptCluster groups related ConceptNodes based on ontology domain structures
    and Jaccard file co-membership coupling.
    """

    id: uuid.UUID
    """Unique identifier for this cluster."""

    cluster_key: str
    """Unique search key for the cluster (e.g. 'identity_access_mgmt')."""

    cluster_label: str
    """Human-friendly display name (e.g. 'Identity & Access Management')."""

    cohesion_score: float
    """Strength of dynamic file-overlap coupling [0.00, 1.00]."""

    member_count: int = 0
    """Number of concepts grouped in this cluster."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Dynamic structural centroid and community modularity details."""

    created_at: datetime = field(default_factory=datetime.utcnow)
    """Timestamp when this cluster was created."""

    updated_at: datetime = field(default_factory=datetime.utcnow)
    """Timestamp when this cluster was last updated."""

    def validate(self) -> None:
        """
        Validate ConceptCluster invariants.

        Raises:
            InvalidEntityException: If out of bounds.
        """
        if not self.cluster_key or not self.cluster_key.strip():
            raise InvalidEntityException("cluster_key must not be empty.")
        if not self.cluster_label or not self.cluster_label.strip():
            raise InvalidEntityException("cluster_label must not be empty.")
        if not (0.00 <= self.cohesion_score <= 1.00):
            raise InvalidEntityException("cohesion_score must be in [0.00, 1.00].")
        if self.member_count < 0:
            raise InvalidEntityException("member_count must be non-negative.")
