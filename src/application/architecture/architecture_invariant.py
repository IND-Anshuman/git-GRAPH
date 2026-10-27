"""Domain model representing architectural invariants."""

from dataclasses import dataclass

from .architecture_violation import ViolationSeverity


@dataclass(frozen=True)
class ArchitectureInvariant:
    """An architectural rule or invariant that must be maintained."""

    name: str
    description: str
    rule_expression: str
    severity: ViolationSeverity
    enabled: bool = True
    source_role: str | None = None
    forbidden_target_role: str | None = None
