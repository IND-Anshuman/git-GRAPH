from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class DecisionFitness:
    decision_id: UUID
    longevity_score: float
    stability_score: float
    impact_score: float
    adoption_score: float
    success_rate: float
    overall_fitness: float
    evaluated_at: datetime
