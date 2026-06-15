"""Governance workflow engine for capability candidates and lifecycle management."""

import uuid
from typing import Dict, List, Any
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.capabilities.capability_candidate import CapabilityCandidate
from src.application.capabilities.capability import Capability
from src.application.capabilities.capability_type import CapabilityType

class CapabilityGovernanceEngine:
    """Manages manual and automated governance transitions (approve, reject, merge, split, rename)."""

    def approve_candidate(self, uow: IUnitOfWork, candidate: CapabilityCandidate) -> Capability:
        """Promotes a candidate to an active, verified system capability."""
        candidate.status = "APPROVED"
        cap = Capability(
            id=candidate.id,
            name=candidate.name,
            description=candidate.description,
            confidence=candidate.confidence,
            concepts=candidate.evidence.concepts,
            behaviors=candidate.evidence.behaviors,
            flows=candidate.evidence.flows,
            entities=candidate.evidence.entities,
            relationships=candidate.evidence.supporting_relationships,
            capability_type=CapabilityType[candidate.capability_type] if candidate.capability_type in CapabilityType.__members__ else CapabilityType.TECHNICAL
        )
        return cap

    def reject_candidate(self, uow: IUnitOfWork, candidate: CapabilityCandidate) -> None:
        """Flags a candidate as rejected to prevent further automated promotion."""
        candidate.status = "REJECTED"

    def merge_capabilities(self, uow: IUnitOfWork, cap_a: Capability, cap_b: Capability, name: str) -> Capability:
        """Combines two overlapping capabilities into a single consolidated capability."""
        merged_id = uuid.uuid4()
        merged = Capability(
            id=merged_id,
            name=name,
            description=f"Merged capability from {cap_a.name} and {cap_b.name}",
            confidence=max(cap_a.confidence, cap_b.confidence),
            concepts=list(set(cap_a.concepts + cap_b.concepts)),
            behaviors=list(set(cap_a.behaviors + cap_b.behaviors)),
            flows=list(set(cap_a.flows + cap_b.flows)),
            entities=list(set(cap_a.entities + cap_b.entities)),
            relationships=list(set(cap_a.relationships + cap_b.relationships)),
            capability_type=cap_a.capability_type
        )
        return merged
