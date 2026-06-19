"""Domain model representing architecture fitness metrics."""

from dataclasses import dataclass, field

@dataclass(frozen=True)
class ArchitectureFitness:
    """Fitness metrics evaluating the health of the architecture. All scores are in [0.0, 1.0]."""
    coupling_score: float
    cohesion_score: float
    instability_score: float
    abstractness_score: float
    distance_from_main_sequence: float
    cyclicity_score: float
    layer_violation_score: float
    overall_score: float
    formulas: dict[str, str] = field(default_factory=dict)
