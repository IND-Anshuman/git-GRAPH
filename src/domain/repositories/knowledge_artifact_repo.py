from abc import ABC, abstractmethod
import uuid
from typing import List, Optional
from src.domain.entities.knowledge_artifact import KnowledgeArtifact

class IKnowledgeArtifactRepository(ABC):
    """Interface for KnowledgeArtifact repository operations."""

    @abstractmethod
    def save(self, artifact: KnowledgeArtifact) -> None:
        """Persist a single knowledge artifact."""
        pass

    @abstractmethod
    def save_batch(self, artifacts: List[KnowledgeArtifact]) -> None:
        """Persist multiple knowledge artifacts in a single batch."""
        pass

    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> Optional[KnowledgeArtifact]:
        """Fetch a knowledge artifact by its ID."""
        pass

    @abstractmethod
    def list_by_repository(self, repository_id: uuid.UUID) -> List[KnowledgeArtifact]:
        """List all artifacts associated with a repository."""
        pass

    @abstractmethod
    def list_by_commit(self, repository_id: uuid.UUID, commit_hash: str) -> List[KnowledgeArtifact]:
        """List all artifacts created/observed at a specific commit."""
        pass

    @abstractmethod
    def get_active_artifacts_at_commit(self, repository_id: uuid.UUID, commit_hashes: List[str]) -> List[KnowledgeArtifact]:
        """Fetch all artifacts that are active (valid) for any commit in the list of ancestors."""
        pass
