"""Cohesion calculation engine for capabilities."""

from typing import Dict, Any

class CapabilityCohesionEngine:
    """Evaluates the internal cohesion (flow density, concept agreement, behavior similarity) within a single capability."""

    def compute_cohesion(
        self,
        internal_flow_density: float,
        internal_concept_similarity: float,
        internal_behavior_similarity: float
    ) -> Dict[str, Any]:
        """
        Calculates cohesion score:
        0.40 * Flow Density + 0.40 * Concept Similarity + 0.20 * Behavior Similarity
        """
        cohesion_score = round(
            internal_flow_density * 0.40 +
            internal_concept_similarity * 0.40 +
            internal_behavior_similarity * 0.20,
            3
        )
        return {
            "internal_flow_density": internal_flow_density,
            "internal_concept_similarity": internal_concept_similarity,
            "internal_behavior_similarity": internal_behavior_similarity,
            "cohesion_score": cohesion_score
        }
