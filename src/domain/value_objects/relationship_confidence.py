from dataclasses import dataclass

@dataclass(frozen=True)
class RelationshipConfidence:
    """Confidence scoring breakdown for inferred relationships."""
    structural_score: float
    framework_score: float
    naming_score: float
    flow_score: float
    final_score: float
