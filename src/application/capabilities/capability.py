"""Domain model representing a system capability."""

import uuid
from dataclasses import dataclass, field

from src.application.capabilities.capability_coverage import CapabilityCoverage
from src.application.capabilities.capability_type import CapabilityType


@dataclass
class Capability:
    """The aggregate root representing a discovered and mapped system capability."""

    id: uuid.UUID
    name: str
    description: str
    confidence: float
    concepts: list[str] = field(default_factory=list)
    behaviors: list[str] = field(default_factory=list)
    flows: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)
    capability_type: CapabilityType = CapabilityType.TECHNICAL
    maturity_score: float = 0.0
    risk_score: float = 0.0
    coverage_score: float = 0.0
    coverage: CapabilityCoverage = field(default_factory=CapabilityCoverage)

    def validate(self) -> None:
        """Validates invariants of the Capability."""
        if not self.name or not self.name.strip():
            raise ValueError("Capability.name must not be empty.")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Capability.confidence must be in [0.0, 1.0].")
        if not (0.0 <= self.maturity_score <= 1.0):
            raise ValueError("Capability.maturity_score must be in [0.0, 1.0].")
        if not (0.0 <= self.risk_score <= 1.0):
            raise ValueError("Capability.risk_score must be in [0.0, 1.0].")
        if not (0.0 <= self.coverage_score <= 1.0):
            raise ValueError("Capability.coverage_score must be in [0.0, 1.0].")
