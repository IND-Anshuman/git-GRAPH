"""Engine for identifying and modeling Bounded Contexts."""

import uuid
from typing import Dict, List, Set, Any
from .architecture_graph import ArchitectureGraph, ArchitectureNode, ArchitectureEdge

class BoundedContextEngine:
    """Identifies and injects Bounded Context nodes into the architecture graph."""

    def identify_contexts(self, graph: ArchitectureGraph) -> None:
        """
        Analyzes the graph to detect Bounded Contexts, adds them as explicit
        ArchitectureNode instances, and links them to their constituent nodes.
        
        This mutates the provided graph.
        """
        if not graph.nodes:
            return

        # Simple heuristic: cluster nodes based on their directory path, 
        # namespace, or explicit metadata.
        # For this implementation, we will use a hypothetical "namespace" or "module" 
        # in node metadata. If unavailable, fallback to connected components or just one context.
        
        context_map: Dict[str, List[ArchitectureNode]] = {}
        
        for node in graph.nodes.values():
            # Skip already identified bounded contexts
            if node.node_type == "BoundedContext":
                continue
                
            # Attempt to group by domain, module, or namespace
            domain = node.metadata.get("domain", node.metadata.get("module", "Core"))
            
            if domain not in context_map:
                context_map[domain] = []
            context_map[domain].append(node)
            
        # Add bounded context nodes and edges
        for domain, group_nodes in context_map.items():
            context_id = f"ctx-{uuid.uuid4().hex[:8]}"
            
            context_node = ArchitectureNode(
                node_id=context_id,
                node_type="BoundedContext",
                label=f"{domain} Context",
                metadata={"domain": domain, "auto_detected": True}
            )
            
            graph.add_node(context_node)
            
            for child_node in group_nodes:
                edge = ArchitectureEdge(
                    from_id=context_id,
                    to_id=child_node.node_id,
                    relationship="CONTAINS"
                )
                graph.add_edge(edge)
