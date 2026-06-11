from dataclasses import dataclass

@dataclass(frozen=True)
class DependencyNode:
    id: str
    name: str
    version: str | None
    dependency_type: str  # package, module, library

@dataclass(frozen=True)
class DependencyEdge:
    source_id: str
    target_id: str
    edge_type: str
