"""Stability index calculation engine for capabilities."""

class CapabilityStabilityEngine:
    """Calculates capability stability over time based on drift and change frequency metrics."""

    def compute_stability(self, drift: float, change_frequency: float, dependency_churn: float) -> dict:
        """
        Compute stability rating using:
        1.0 - (0.40 * drift + 0.40 * change_frequency + 0.20 * dependency_churn)
        
        Classifies rating into: STABLE (>= 0.80), EVOLVING (>= 0.50), or VOLATILE (< 0.50).
        """
        total_churn = drift * 0.40 + change_frequency * 0.40 + dependency_churn * 0.20
        stability_score = round(max(0.0, min(1.0, 1.0 - total_churn)), 3)

        if stability_score >= 0.8:
            status = "STABLE"
        elif stability_score >= 0.5:
            status = "EVOLVING"
        else:
            status = "VOLATILE"

        return {
            "score": stability_score,
            "status": status
        }
