"""Risk calculation engine for capabilities."""

from typing import Dict, Any

class CapabilityRiskEngine:
    """Calculates capability risk index using weighted structural, operational, and dependency metrics."""

    def compute_risk(
        self,
        dependency_risk: float,
        complexity_risk: float,
        change_frequency: float,
        ownership_risk: float,
        coverage_gaps: float,
        external_dependency_risk: float
    ) -> Dict[str, Any]:
        """
        Compute risk rating based on:
        - 0.25 Dependency Risk
        - 0.20 Complexity Risk
        - 0.20 Change Frequency
        - 0.15 Ownership Risk
        - 0.10 Coverage Gaps
        - 0.10 External Dependency Risk
        
        Outputs score and ratings: LOW, MEDIUM, HIGH, or CRITICAL.
        """
        score = (
            dependency_risk * 0.25 +
            complexity_risk * 0.20 +
            change_frequency * 0.20 +
            ownership_risk * 0.15 +
            coverage_gaps * 0.10 +
            external_dependency_risk * 0.10
        )
        score = round(max(0.0, min(1.0, score)), 3)

        if score >= 0.80:
            rating = "CRITICAL"
        elif score >= 0.60:
            rating = "HIGH"
        elif score >= 0.35:
            rating = "MEDIUM"
        else:
            rating = "LOW"

        return {
            "score": score,
            "risk_rating": rating,
            "dimensions": {
                "dependency_risk": dependency_risk,
                "complexity_risk": complexity_risk,
                "change_frequency": change_frequency,
                "ownership_risk": ownership_risk,
                "coverage_gaps": coverage_gaps,
                "external_dependency_risk": external_dependency_risk
            }
        }
