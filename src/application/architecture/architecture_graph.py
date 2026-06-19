"""Domain model representing the architecture graph."""

from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class ArchitectureNode:
    """A node in the architecture graph."""
    node_id: str
    node_type: str  # Architecture | Capability | Service | BoundedContext | Team | ...
    label: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ArchitectureEdge:
    """An edge representing a relationship in the architecture graph."""
    from_id: str
    to_id: str
    relationship: str  # OWNS | DEPENDS_ON | IMPLEMENTS | CONTAINS | USES | EXPOSES | PROVIDES | CONSUMES | SUPERVISES

class ArchitectureGraph:
    """Graph structure optimized for architectural reasoning."""
    
    def __init__(self) -> None:
        """Initialize the architecture graph."""
        self.nodes: Dict[str, ArchitectureNode] = {}
        self.edges: List[ArchitectureEdge] = []
        
    def add_node(self, node: ArchitectureNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.node_id] = node
        
    def add_edge(self, edge: ArchitectureEdge) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)
        
    def get_neighbors(self, node_id: str, relationship: str = None) -> List[str]:
        """Get neighboring nodes for a given node, optionally filtered by relationship type."""
        neighbors = []
        for edge in self.edges:
            if edge.from_id == node_id:
                if relationship is None or edge.relationship == relationship:
                    neighbors.append(edge.to_id)
            elif edge.to_id == node_id:
                if relationship is None or edge.relationship == relationship:
                    neighbors.append(edge.from_id)
        return list(set(neighbors))

    def to_dict(self) -> Dict[str, Any]:
        """Convert the graph to a dictionary representation."""
        return {
            "nodes": [
                {
                    "node_id": node.node_id,
                    "node_type": node.node_type,
                    "label": node.label,
                    "metadata": node.metadata
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "from_id": edge.from_id,
                    "to_id": edge.to_id,
                    "relationship": edge.relationship
                }
                for edge in self.edges
            ]
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArchitectureGraph":
        """Create a graph from a dictionary representation."""
        graph = cls()
        for node_data in data.get("nodes", []):
            graph.add_node(ArchitectureNode(**node_data))
        for edge_data in data.get("edges", []):
            graph.add_edge(ArchitectureEdge(**edge_data))
        return graph

    def detect_cycles(self) -> List[List[str]]:
        """Detect cyclic dependencies in the graph."""
        # TODO: Implement cycle detection logic (Tarjan's or similar)
        return []

    def fan_in(self, node_id: str) -> int:
        """Calculate the fan-in (number of incoming edges) for a node."""
        return sum(1 for edge in self.edges if edge.to_id == node_id)

    def fan_out(self, node_id: str) -> int:
        """Calculate the fan-out (number of outgoing edges) for a node."""
        return sum(1 for edge in self.edges if edge.from_id == node_id)

    def compute_layer_violations(self, layer_order: List[str]) -> int:
        """Compute the number of edges that violate the given layer order."""
        layer_indices = {layer: idx for idx, layer in enumerate(layer_order)}
        violations = 0
        
        for edge in self.edges:
            from_node = self.nodes.get(edge.from_id)
            to_node = self.nodes.get(edge.to_id)
            
            if from_node and to_node:
                from_layer = from_node.metadata.get("layer")
                to_layer = to_node.metadata.get("layer")
                
                if from_layer in layer_indices and to_layer in layer_indices:
                    # If the from_layer is 'lower' (higher index) than the to_layer, it's a violation.
                    if layer_indices[from_layer] > layer_indices[to_layer]:
                        violations += 1
                        
        return violations
