"""Hierarchy placement engine for capabilities."""

class CapabilityPlacementEngine:
    """Calculates hierarchy placement score for classifying capabilities inside dynamic taxonomy structures."""

    def place_capability(
        self,
        concept_similarity: float,
        flow_similarity: float,
        behavior_similarity: float,
        usage_coverage: float
    ) -> float:
        """
        Compute placement score using:
        0.35 * Concept Similarity + 0.30 * Flow Similarity + 0.20 * Behavior Similarity + 0.15 * Usage Coverage
        """
        score = (
            concept_similarity * 0.35 +
            flow_similarity * 0.30 +
            behavior_similarity * 0.20 +
            usage_coverage * 0.15
        )
        return round(max(0.0, min(1.0, score)), 3)
