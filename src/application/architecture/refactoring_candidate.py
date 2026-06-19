"""Domain model representing refactoring candidates based on structural analysis."""

import uuid
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field

class RefactoringCandidateType(str, Enum):
    """Types of refactoring candidates."""
    GOD_CLASS = "GOD_CLASS"
    BLOB_SERVICE = "BLOB_SERVICE"
    FEATURE_ENVY = "FEATURE_ENVY"
    SHOTGUN_SURGERY = "SHOTGUN_SURGERY"
    LARGE_METHOD = "LARGE_METHOD"
    CYCLE = "CYCLE"
    LOW_COHESION = "LOW_COHESION"
    HIGH_COUPLING = "HIGH_COUPLING"
    ARCHITECTURE_VIOLATION = "ARCHITECTURE_VIOLATION"
    CAPABILITY_OVERLOAD = "CAPABILITY_OVERLOAD"
    SERVICE_OVERLOAD = "SERVICE_OVERLOAD"

class RefactoringPriority(str, Enum):
    """Priority levels for refactoring."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class RefactoringCandidate:
    """A detected refactoring candidate with associated evidence and expected benefit."""
    id: uuid.UUID
    candidate_type: RefactoringCandidateType
    priority: RefactoringPriority
    target_entities: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)
    expected_benefit: str = ""
    fitness_impact: float = 0.0
    detected_at: datetime = field(default_factory=datetime.utcnow)
