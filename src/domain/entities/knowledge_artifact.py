from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import Any

@dataclass
class KnowledgeArtifact:
    """Universal versioned storage model for all compiler, discovery, and reasoning metadata."""
    id: uuid.UUID
    repository_id: uuid.UUID
    artifact_type: str  # 'entity', 'relationship', 'behavior', 'concept', 'capability', 'contract'
    source: str         # 'extraction', 'compiler', 'discovery', 'llm'
    confidence: float
    valid_from_commit: str
    valid_to_commit: str | None
    observed_at: datetime
    artifact_version: int
    provenance: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validates the invariants of the KnowledgeArtifact."""
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("KnowledgeArtifact.confidence must be in range [0.0, 1.0]")
        if not self.valid_from_commit:
            raise ValueError("KnowledgeArtifact.valid_from_commit must not be empty")
        if self.artifact_version < 1:
            raise ValueError("KnowledgeArtifact.artifact_version must be >= 1")
