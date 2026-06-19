"""Domain model representing evidence supporting an architecture discovery."""

from dataclasses import dataclass, field

@dataclass
class ArchitectureEvidence:
    """Aggregated evidence that justifies the detection of an architectural style."""
    capabilities: list[dict] = field(default_factory=list)
    flows: list[dict] = field(default_factory=list)
    entities: list[dict] = field(default_factory=list)
    relationships: list[dict] = field(default_factory=list)
    dependency_paths: list[list[str]] = field(default_factory=list)
    ownership_paths: list[list[str]] = field(default_factory=list)
    supporting_patterns: list[str] = field(default_factory=list)
    violating_patterns: list[str] = field(default_factory=list)
