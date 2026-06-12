"""Abstract repository interfaces for all Concept Graph persistence operations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import uuid

from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.entities.concept_relationship import ConceptRelationship
from src.domain.entities.concept_cluster import ConceptCluster
from src.domain.entities.concept_explanation import ConceptExplanation
from src.domain.entities.concept_evolution import ConceptEvolution
from src.domain.entities.concept_metrics import ConceptMetrics
from src.domain.entities.concept_drift import ConceptDrift
from src.domain.enums.concept_relationship_type import ConceptRelationshipType
from src.domain.value_objects.repository_id import RepositoryId


class IConceptNodeRepository(ABC):
    """Port defining persistence operations for ConceptNode domain entities."""

    @abstractmethod
    def save(self, node: ConceptNode) -> None:
        """Persist a single ConceptNode, inserting or updating."""
        pass

    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> Optional[ConceptNode]:
        """Retrieve a ConceptNode by its primary key UUID."""
        pass

    @abstractmethod
    def get_by_ontology_node(self, repository_id: RepositoryId, ontology_node_id: str) -> Optional[ConceptNode]:
        """Retrieve a ConceptNode by its repository and ontology path key."""
        pass

    @abstractmethod
    def list_by_repository(self, repository_id: RepositoryId) -> List[ConceptNode]:
        """List all ConceptNodes registered for a repository."""
        pass

    @abstractmethod
    def delete_by_repository(self, repository_id: RepositoryId) -> None:
        """Delete all ConceptNodes for a repository."""
        pass


class IConceptVersionRepository(ABC):
    """Port defining persistence operations for ConceptVersion domain entities."""

    @abstractmethod
    def save(self, version: ConceptVersion) -> None:
        """Persist a single ConceptVersion."""
        pass

    @abstractmethod
    def save_batch(self, versions: List[ConceptVersion]) -> None:
        """Persist multiple ConceptVersions in batch."""
        pass

    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> Optional[ConceptVersion]:
        """Retrieve a ConceptVersion by its primary key UUID."""
        pass

    @abstractmethod
    def get_by_concept_at_commit(self, concept_id: uuid.UUID, commit_hash: str) -> Optional[ConceptVersion]:
        """Retrieve a ConceptVersion snapshot for a concept at a specific commit."""
        pass

    @abstractmethod
    def list_by_concept(self, concept_id: uuid.UUID) -> List[ConceptVersion]:
        """List all historical versions of a concept."""
        pass

    @abstractmethod
    def list_by_commit(self, commit_hash: str) -> List[ConceptVersion]:
        """List all active ConceptVersions at a specific commit."""
        pass


class IConceptEvidenceRepository(ABC):
    """Port defining persistence operations for ConceptEvidence domain entities."""

    @abstractmethod
    def save_batch(self, evidence_list: List[ConceptEvidence]) -> None:
        """Persist multiple ConceptEvidence rows in batch."""
        pass

    @abstractmethod
    def list_by_concept_version(self, concept_version_id: uuid.UUID) -> List[ConceptEvidence]:
        """List all evidence entries supporting a specific concept version."""
        pass

    @abstractmethod
    def delete_by_concept_version(self, concept_version_id: uuid.UUID) -> None:
        """Delete evidence for a concept version."""
        pass


class IConceptRelationshipRepository(ABC):
    """Port defining persistence operations for ConceptRelationship domain entities."""

    @abstractmethod
    def save(self, relationship: ConceptRelationship) -> None:
        """Persist a single ConceptRelationship."""
        pass

    @abstractmethod
    def save_batch(self, relationships: List[ConceptRelationship]) -> None:
        """Persist multiple ConceptRelationships in batch."""
        pass

    @abstractmethod
    def list_by_commit(self, commit_hash: str) -> List[ConceptRelationship]:
        """List all ConceptRelationships at a specific commit."""
        pass

    @abstractmethod
    def delete_by_commit(self, repository_id: RepositoryId, commit_hash: str) -> None:
        """Delete concept relationships at a specific commit."""
        pass


class IConceptClusterRepository(ABC):
    """Port defining persistence operations for ConceptCluster domain entities."""

    @abstractmethod
    def save(self, cluster: ConceptCluster) -> None:
        """Persist a single ConceptCluster."""
        pass

    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> Optional[ConceptCluster]:
        """Retrieve a ConceptCluster by its primary key UUID."""
        pass

    @abstractmethod
    def get_by_key(self, cluster_key: str) -> Optional[ConceptCluster]:
        """Retrieve a ConceptCluster by its unique lookup key."""
        pass

    @abstractmethod
    def list_all(self) -> List[ConceptCluster]:
        """List all registered concept clusters."""
        pass

    @abstractmethod
    def add_member(self, cluster_id: uuid.UUID, concept_id: uuid.UUID) -> None:
        """Link a concept node to a cluster (inserts a cluster membership row)."""
        pass

    @abstractmethod
    def remove_member(self, cluster_id: uuid.UUID, concept_id: uuid.UUID) -> None:
        """Remove a concept node link from a cluster."""
        pass

    @abstractmethod
    def get_concept_memberships(self, concept_id: uuid.UUID) -> List[ConceptCluster]:
        """Retrieve all clusters that a specific concept belongs to."""
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """Delete all clusters and memberships."""
        pass


class IConceptExplanationRepository(ABC):
    """Port defining persistence operations for ConceptExplanation domain entities."""

    @abstractmethod
    def save(self, explanation: ConceptExplanation) -> None:
        """Persist a single ConceptExplanation."""
        pass

    @abstractmethod
    def get_by_concept_version(self, concept_version_id: uuid.UUID) -> Optional[ConceptExplanation]:
        """Retrieve the explanation details for a ConceptVersion."""
        pass


class IConceptMetricsRepository(ABC):
    """Port defining persistence operations for ConceptMetrics domain entities."""

    @abstractmethod
    def save(self, metrics: ConceptMetrics) -> None:
        """Persist a single ConceptMetrics entry."""
        pass

    @abstractmethod
    def save_batch(self, metrics_list: List[ConceptMetrics]) -> None:
        """Persist multiple ConceptMetrics entries in batch."""
        pass

    @abstractmethod
    def get_by_concept_version(self, concept_version_id: uuid.UUID) -> Optional[ConceptMetrics]:
        """Retrieve the metrics details for a ConceptVersion."""
        pass


class IConceptEvolutionRepository(ABC):
    """Port defining persistence operations for ConceptEvolution domain entities."""

    @abstractmethod
    def save(self, evolution: ConceptEvolution) -> None:
        """Persist a single ConceptEvolution transition link."""
        pass

    @abstractmethod
    def save_batch(self, evolutions: List[ConceptEvolution]) -> None:
        """Persist multiple ConceptEvolution links in batch."""
        pass

    @abstractmethod
    def list_by_to_version(self, to_concept_version_id: uuid.UUID) -> List[ConceptEvolution]:
        """List evolution transitions entering a target concept version."""
        pass

    @abstractmethod
    def list_by_concept_timeline(self, concept_id: uuid.UUID) -> List[ConceptEvolution]:
        """List all evolution transitions along the history timeline of a concept node."""
        pass


class IConceptDriftRepository(ABC):
    """Port defining persistence operations for ConceptDrift domain entities."""

    @abstractmethod
    def save(self, drift: ConceptDrift) -> None:
        """Persist a single ConceptDrift entry."""
        pass

    @abstractmethod
    def get_by_concept_and_commits(self, concept_id: uuid.UUID, baseline_commit: str, current_commit: str) -> Optional[ConceptDrift]:
        """Retrieve a specific drift record for a concept between two commits."""
        pass

    @abstractmethod
    def list_by_concept(self, concept_id: uuid.UUID) -> List[ConceptDrift]:
        """List all drift records associated with a ConceptNode."""
        pass

