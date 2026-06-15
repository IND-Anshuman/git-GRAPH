"""Confidence evaluation engine for capabilities."""

class CapabilityConfidenceEngine:
    """Calculates unified confidence score for discovered capability candidates using evidence metrics."""

    def compute_confidence(self, candidate) -> float:
        """
        Compute confidence score based on:
        - 0.30 Evidence Strength
        - 0.25 Flow Cohesion
        - 0.20 Concept Agreement
        - 0.15 Behavior Agreement
        - 0.10 Relationship Density
        """
        evidence = candidate.evidence
        if not evidence:
            return 0.5

        # 1. Evidence Strength: count of concepts + behaviors relative to a baseline of 10
        total_items = len(evidence.concepts) + len(evidence.behaviors)
        evidence_strength = min(1.0, total_items / 10.0) if total_items > 0 else 0.5

        # 2. Flow Cohesion: frequency of mapped flows (max 5 -> 1.0)
        flow_cohesion = min(1.0, len(evidence.flows) / 5.0) if evidence.flows else 0.5

        # 3. Concept Agreement: density or agreement (default 0.8, or 1.0 if highly cohesive)
        concept_agreement = 0.8 if len(evidence.concepts) > 1 else 1.0

        # 4. Behavior Agreement: consistency of behaviors (default 0.8, or 1.0 if single focus)
        behavior_agreement = 0.8 if len(evidence.behaviors) > 1 else 1.0

        # 5. Relationship Density: count of supporting relationships (max 5 -> 1.0)
        relationship_density = min(1.0, len(evidence.supporting_relationships) / 5.0) if evidence.supporting_relationships else 0.5

        score = (
            0.30 * evidence_strength +
            0.25 * flow_cohesion +
            0.20 * concept_agreement +
            0.15 * behavior_agreement +
            0.10 * relationship_density
        )
        return round(min(1.0, max(0.0, score)), 3)
