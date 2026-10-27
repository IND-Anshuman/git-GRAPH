"""Domain model representing the architecture graph."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ArchitectureNode:
    """A node in the architecture graph."""

    node_id: str
    node_type: str  # Architecture | Capability | Service | BoundedContext | Team | ...
    label: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchitectureEdge:
    """An edge representing a relationship in the architecture graph."""

    from_id: str
    to_id: str
    relationship: (
        str  # OWNS | DEPENDS_ON | IMPLEMENTS | CONTAINS | USES | EXPOSES | PROVIDES | CONSUMES | SUPERVISES
    )


class ArchitectureGraph:
    """Graph structure optimized for architectural reasoning."""

    def __init__(self) -> None:
        """Initialize the architecture graph."""
        self.nodes: dict[str, ArchitectureNode] = {}
        self.edges: list[ArchitectureEdge] = []

    def add_node(self, node: ArchitectureNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.node_id] = node

    def add_edge(self, edge: ArchitectureEdge) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)

    def get_neighbors(self, node_id: str, relationship: str | None = None) -> list[str]:
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

    def to_dict(self) -> dict[str, Any]:
        """Convert the graph to a dictionary representation."""
        return {
            "nodes": [
                {
                    "node_id": node.node_id,
                    "node_type": node.node_type,
                    "label": node.label,
                    "metadata": node.metadata,
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {"from_id": edge.from_id, "to_id": edge.to_id, "relationship": edge.relationship}
                for edge in self.edges
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArchitectureGraph":
        """Create a graph from a dictionary representation."""
        graph = cls()
        for node_data in data.get("nodes", []):
            graph.add_node(ArchitectureNode(**node_data))
        for edge_data in data.get("edges", []):
            graph.add_edge(ArchitectureEdge(**edge_data))
        return graph

    # Hierarchical edges describe nesting, not dependency, so a module that
    # CONTAINS a class which imports the module is not a dependency cycle.
    NON_DEPENDENCY_RELATIONSHIPS = frozenset({"CONTAINS", "OWNS", "SUPERVISES", "DEFINES", "DECLARES"})

    def detect_cycles(self) -> list[list[str]]:
        """Return every dependency cycle as a strongly connected component.

        Uses Tarjan's algorithm (iterative, so deep graphs cannot overflow the
        recursion limit) over directed dependency edges. Each returned list is
        one SCC with more than one node, or a single node with a self-loop,
        sorted for deterministic output. Runs in O(V + E).
        """
        adjacency: dict[str, list[str]] = {node_id: [] for node_id in self.nodes}
        self_loops: set[str] = set()
        for edge in self.edges:
            if edge.relationship in self.NON_DEPENDENCY_RELATIONSHIPS:
                continue
            adjacency.setdefault(edge.from_id, []).append(edge.to_id)
            adjacency.setdefault(edge.to_id, [])
            if edge.from_id == edge.to_id:
                self_loops.add(edge.from_id)

        index_of: dict[str, int] = {}
        lowlink: dict[str, int] = {}
        on_stack: set[str] = set()
        stack: list[str] = []
        components: list[list[str]] = []
        counter = 0

        for root in adjacency:
            if root in index_of:
                continue
            work: list[tuple[str, int]] = [(root, 0)]
            while work:
                node, child_pos = work.pop()
                if child_pos == 0:
                    index_of[node] = lowlink[node] = counter
                    counter += 1
                    stack.append(node)
                    on_stack.add(node)
                children = adjacency[node]
                if child_pos < len(children):
                    work.append((node, child_pos + 1))
                    child = children[child_pos]
                    if child not in index_of:
                        work.append((child, 0))
                    elif child in on_stack:
                        lowlink[node] = min(lowlink[node], index_of[child])
                    continue
                # All children done: propagate lowlink to the parent frame.
                if work:
                    parent = work[-1][0]
                    lowlink[parent] = min(lowlink[parent], lowlink[node])
                if lowlink[node] == index_of[node]:
                    component: list[str] = []
                    while True:
                        member = stack.pop()
                        on_stack.discard(member)
                        component.append(member)
                        if member == node:
                            break
                    if len(component) > 1 or node in self_loops:
                        components.append(sorted(component))

        return sorted(components, key=lambda c: (-len(c), c))

    def fan_in(self, node_id: str) -> int:
        """Calculate the fan-in (number of incoming edges) for a node."""
        return sum(1 for edge in self.edges if edge.to_id == node_id)

    def fan_out(self, node_id: str) -> int:
        """Calculate the fan-out (number of outgoing edges) for a node."""
        return sum(1 for edge in self.edges if edge.from_id == node_id)

    def compute_layer_violations(self, layer_order: list[str]) -> int:
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
