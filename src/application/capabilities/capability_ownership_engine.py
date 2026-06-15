"""Ownership resolution engine for capabilities."""

import uuid
from typing import Dict, List, Any
from src.application.ports.unit_of_work import IUnitOfWork

class CapabilityOwnershipEngine:
    """Auto-resolves capability ownership links (Team, Service, Bounded Context, Microservice, Agent Team)."""

    def resolve_owners(self, uow: IUnitOfWork, repository_id: uuid.UUID, capability: Any) -> List[Dict[str, Any]]:
        """
        Maps a capability to owning teams, services, or contexts based on heuristics.
        Fallbacks to static heuristics for payments, auth, and AI workflows.
        """
        owners = []
        name_lower = capability.name.lower()

        if "auth" in name_lower or "security" in name_lower or "cryptography" in name_lower:
            owners.append({"owner_type": "Team", "owner_name": "Security Team"})
            owners.append({"owner_type": "Service", "owner_name": "Identity Service"})
            owners.append({"owner_type": "Bounded Context", "owner_name": "Identity"})
        elif "pay" in name_lower or "billing" in name_lower or "checkout" in name_lower or "order" in name_lower:
            owners.append({"owner_type": "Team", "owner_name": "Commerce Team"})
            owners.append({"owner_type": "Service", "owner_name": "Payment Service"})
            owners.append({"owner_type": "Bounded Context", "owner_name": "Checkout"})
        elif "retrieve" in name_lower or "agent" in name_lower or "memory" in name_lower or "prompt" in name_lower or "ai" in name_lower:
            owners.append({"owner_type": "Team", "owner_name": "AI Platform Team"})
            owners.append({"owner_type": "Service", "owner_name": "Agent Coordinator Service"})
            owners.append({"owner_type": "Agent Team", "owner_name": "AI Specialist Agents"})
        else:
            owners.append({"owner_type": "Team", "owner_name": "Core Platform Team"})
            owners.append({"owner_type": "Service", "owner_name": "SaaS Monolith App"})

        return owners
