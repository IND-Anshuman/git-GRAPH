"""Domain entity representing size, coupling, and centrality metrics for a concept version."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from src.domain.exceptions import InvalidEntityException


@dataclass
class ConceptMetrics:
    """
    ConceptMetrics holds topological graph centralities and structural size values
    computed for a ConceptVersion.
    """

    id: uuid.UUID
    """Unique identifier for these metrics."""

    concept_version_id: uuid.UUID
    """The associated ConceptVersion ID."""

    entity_count: int
    """Number of code entities implementing this concept version."""

    file_count: int
    """Number of files containing code entities implementing this concept version."""

    in_degree: int
    """Number of incoming dependency edges (other concepts depending on this one)."""

    out_degree: int
    """Number of outgoing dependency edges (concepts this one depends on)."""

    degree_centrality: float
    """Normalized degree centrality score."""

    betweenness_centrality: float
    """Normalized betweenness centrality score."""

    pagerank_score: float
    """PageRank score computed on the concept dependency graph."""

    impact_score: float
    """Structural impact score of this concept version."""

    computed_at: datetime = field(default_factory=datetime.utcnow)
    """Timestamp when metrics were computed."""

    def validate(self) -> None:
        """
        Validate ConceptMetrics invariants.

        Raises:
            InvalidEntityException: If metrics are negative.
        """
        if self.entity_count < 0:
            raise InvalidEntityException("entity_count must be non-negative.")
        if self.file_count < 0:
            raise InvalidEntityException("file_count must be non-negative.")
        if self.in_degree < 0 or self.out_degree < 0:
            raise InvalidEntityException("degree counts must be non-negative.")
        if self.degree_centrality < 0.0 or self.betweenness_centrality < 0.0:
            raise InvalidEntityException("centrality scores must be non-negative.")
        if self.pagerank_score < 0.0:
            raise InvalidEntityException("pagerank_score must be non-negative.")
        if self.impact_score < 0.0:
            raise InvalidEntityException("impact_score must be non-negative.")
