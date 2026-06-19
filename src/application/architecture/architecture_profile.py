"""Domain model representing an architecture profile."""

import uuid
from datetime import datetime
from dataclasses import dataclass

from .architecture_type import ArchitectureType
from .architecture_confidence import ArchitectureConfidence
from .architecture_evidence import ArchitectureEvidence

@dataclass
class ArchitectureProfile:
    """A detected architectural profile for a given repository and commit."""
    id: uuid.UUID
    architecture_type: ArchitectureType
    confidence: ArchitectureConfidence
    description: str
    evidence: ArchitectureEvidence
    detected_at: datetime
    repository_id: str
    commit_hash: str
