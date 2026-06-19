"""Domain model representing architectural violations."""

import uuid
from enum import Enum
from dataclasses import dataclass, field

class ViolationSeverity(str, Enum):
    """Severity levels for architectural violations."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class ArchitectureViolation:
    """A violation of an architectural rule or invariant."""
    id: uuid.UUID
    rule_name: str
    severity: ViolationSeverity
    affected_entities: list[str] = field(default_factory=list)
    affected_capabilities: list[str] = field(default_factory=list)
    reason: str = ""
    evidence: dict = field(default_factory=dict)
