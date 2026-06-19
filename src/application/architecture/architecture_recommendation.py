"""Domain model representing architectural recommendations."""

import uuid
from enum import Enum
from dataclasses import dataclass, field

class RecommendationType(str, Enum):
    """Types of architectural recommendations."""
    SPLIT_SERVICE = "SPLIT_SERVICE"
    INTRODUCE_INTERFACE = "INTRODUCE_INTERFACE"
    EXTRACT_CAPABILITY = "EXTRACT_CAPABILITY"
    REMOVE_DEPENDENCY = "REMOVE_DEPENDENCY"
    MERGE_CAPABILITIES = "MERGE_CAPABILITIES"

@dataclass
class ArchitectureRecommendation:
    """Actionable structural recommendation derived from architecture analysis."""
    id: uuid.UUID
    recommendation_type: RecommendationType
    target_elements: list[str] = field(default_factory=list)
    action_description: str = ""
    justification: str = ""
    expected_fitness_delta: float = 0.0
    difficulty: str = "MEDIUM"
