"""Drift engine for evaluating capability mutations across version histories."""

from typing import Dict, Any

class CapabilityDriftEngine:
    """Computes drift metrics for capabilities across multiple structural/behavioral dimensions."""

    def compute_drift(
        self,
        concept_drift: float,
        flow_drift: float,
        behavior_drift: float,
        dependency_drift: float,
        coverage_drift: float
    ) -> Dict[str, Any]:
        """
        Compute weighted aggregate drift:
        - 0.30 Concept Drift
        - 0.25 Flow Drift
        - 0.20 Behavior Drift
        - 0.15 Dependency Drift
        - 0.10 Coverage Drift
        
        Outputs score and categories: TRIVIAL, MINOR, SIGNIFICANT, MAJOR, or COMPLETE.
        """
        drift_score = (
            concept_drift * 0.30 +
            flow_drift * 0.25 +
            behavior_drift * 0.20 +
            dependency_drift * 0.15 +
            coverage_drift * 0.10
        )
        drift_score = round(max(0.0, min(1.0, drift_score)), 3)

        if drift_score >= 0.85:
            category = "COMPLETE"
        elif drift_score >= 0.60:
            category = "MAJOR"
        elif drift_score >= 0.30:
            category = "SIGNIFICANT"
        elif drift_score >= 0.10:
            category = "MINOR"
        else:
            category = "TRIVIAL"

        return {
            "drift_score": drift_score,
            "drift_category": category,
            "dimension_scores": {
                "concept": concept_drift,
                "flow": flow_drift,
                "behavior": behavior_drift,
                "dependency": dependency_drift,
                "coverage": coverage_drift
            }
        }
