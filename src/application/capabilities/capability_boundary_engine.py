"""Boundary strength and leakage detection engine for capabilities."""

from typing import Dict, Any

class CapabilityBoundaryEngine:
    """Evaluates boundaries of a capability to detect leakage, coupling breaches, and define Bounded Context bounds."""

    def compute_boundary(self, internal_entities_count: int, external_dependencies_count: int) -> Dict[str, Any]:
        """
        Calculates boundary strength and leakage metrics based on relative counts of internal entities vs external dependencies.
        """
        total = internal_entities_count + external_dependencies_count
        boundary_strength = round(internal_entities_count / total, 3) if total > 0 else 1.0

        # Heuristic for leakage: dependencies exceed 30% of internal entities
        leakage = external_dependencies_count > (internal_entities_count * 0.3)

        return {
            "internal_entities": internal_entities_count,
            "external_dependencies": external_dependencies_count,
            "boundary_strength": boundary_strength,
            "leakage_detected": leakage
        }
