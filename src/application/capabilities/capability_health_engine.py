"""Health score engine for evaluating capability metrics."""

from typing import Dict, Any

class CapabilityHealthEngine:
    """Computes operational health and code maturity indices for capabilities."""

    def compute_health(self, coverage_score: float, complexity_score: float, coupling_score: float, risk_score: float) -> Dict[str, Any]:
        """
        Calculates maturity score from coverage, complexity, coupling, and risk:
        0.40 * coverage + 0.30 * (1 - complexity) + 0.20 * (1 - coupling) + 0.10 * (1 - risk)
        """
        maturity_score = round(
            coverage_score * 0.40 +
            (1.0 - complexity_score) * 0.30 +
            (1.0 - coupling_score) * 0.20 +
            (1.0 - risk_score) * 0.10,
            3
        )
        return {
            "coverage_score": coverage_score,
            "maturity_score": maturity_score,
            "complexity_score": complexity_score,
            "coupling_score": coupling_score,
            "risk_score": risk_score
        }
