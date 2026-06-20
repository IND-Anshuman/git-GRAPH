from dataclasses import dataclass, field

@dataclass(frozen=True)
class DecisionImpact:
    affected_capabilities: list[str] = field(default_factory=list)
    affected_architectures: list[str] = field(default_factory=list)
    affected_services: list[str] = field(default_factory=list)
    affected_dependencies: list[str] = field(default_factory=list)
    affected_ai_systems: list[str] = field(default_factory=list)
