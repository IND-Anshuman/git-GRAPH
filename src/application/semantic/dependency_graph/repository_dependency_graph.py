"""Domain/Application model representing the Repository Dependency Graph."""

from dataclasses import dataclass, field
import uuid
from typing import Dict, List, Set, Any
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.relationship import Relationship

@dataclass
class RepositoryDependencyGraph:
    """Structure representing the package, module, and external service dependency topology."""
    repository_id: uuid.UUID
    nodes: Dict[str, CodeEntity] = field(default_factory=dict)  # SEID string -> CodeEntity
    edges: List[Relationship] = field(default_factory=list)      # List of dependencies
    external_stubs: Dict[str, CodeEntity] = field(default_factory=dict) # Name -> External Stub Entity

    def add_node(self, entity: CodeEntity) -> None:
        self.nodes[str(entity.seid.value)] = entity

    def add_edge(self, edge: Relationship) -> None:
        self.edges.append(edge)

    def get_dependencies_for(self, seid: str) -> List[CodeEntity]:
        deps = []
        for edge in self.edges:
            if str(edge.source_seid.value) == seid:
                target_str = str(edge.target_seid.value)
                if target_str in self.nodes:
                    deps.append(self.nodes[target_str])
        return deps
