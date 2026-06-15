"""Coupling evaluation engine for capabilities."""

from typing import Dict, Any

class CapabilityCouplingEngine:
    """Evaluates the degree of external coupling (APIs, databases, event channels, shared services) for a capability."""

    def compute_coupling(
        self,
        api_coupling: float,
        database_coupling: float,
        event_coupling: float,
        shared_service_coupling: float,
        shared_entity_coupling: float
    ) -> Dict[str, Any]:
        """
        Calculates coupling score:
        0.25 * API + 0.20 * DB + 0.20 * EVENT + 0.20 * Shared Service + 0.15 * Shared Entity
        """
        coupling_score = round(
            api_coupling * 0.25 +
            database_coupling * 0.20 +
            event_coupling * 0.20 +
            shared_service_coupling * 0.20 +
            shared_entity_coupling * 0.15,
            3
        )
        return {
            "api_coupling": api_coupling,
            "database_coupling": database_coupling,
            "event_coupling": event_coupling,
            "shared_service_coupling": shared_service_coupling,
            "shared_entity_coupling": shared_entity_coupling,
            "coupling_score": coupling_score
        }
