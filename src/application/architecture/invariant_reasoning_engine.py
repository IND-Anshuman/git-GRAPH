"""Engine to evaluate architectural rules and detect violations."""

import uuid
from typing import List, Iterable

from .architecture_graph import ArchitectureGraph
from .architecture_invariant import ArchitectureInvariant
from .architecture_violation import ArchitectureViolation, ViolationSeverity

class InvariantReasoningEngine:
    """Evaluates architectural rules from the built-in invariant set."""

    def evaluate_invariants(
        self,
        graph: ArchitectureGraph,
        invariants: Iterable[ArchitectureInvariant]
    ) -> List[ArchitectureViolation]:
        """
        Evaluate a set of invariants against the given architecture graph.
        Returns a list of violations detected.
        """
        violations: List[ArchitectureViolation] = []
        
        for invariant in invariants:
            if not invariant.enabled:
                continue
                
            # Heuristic invariant evaluation based on roles
            if invariant.source_role and invariant.forbidden_target_role:
                # Find all nodes with the source role
                source_nodes = [
                    node for node in graph.nodes.values()
                    if node.metadata.get("role") == invariant.source_role
                ]
                
                for source_node in source_nodes:
                    # Check its outgoing edges
                    neighbors = graph.get_neighbors(source_node.node_id)
                    for target_id in neighbors:
                        # Check if there is an edge from source to target
                        # get_neighbors returns undirected neighbors, so we should check actual edges
                        has_directed_edge = any(
                            e.from_id == source_node.node_id and e.to_id == target_id
                            for e in graph.edges
                        )
                        
                        if not has_directed_edge:
                            continue
                            
                        target_node = graph.nodes.get(target_id)
                        if target_node and target_node.metadata.get("role") == invariant.forbidden_target_role:
                            violation = ArchitectureViolation(
                                id=uuid.uuid4(),
                                rule_name=invariant.name,
                                severity=invariant.severity,
                                affected_entities=[source_node.node_id, target_id],
                                affected_capabilities=[],
                                reason=f"Node {source_node.label} ({invariant.source_role}) depends on {target_node.label} ({invariant.forbidden_target_role})",
                                evidence={"source_id": source_node.node_id, "target_id": target_id}
                            )
                            violations.append(violation)
                            
            # Other rule expression evaluations can be added here
            # e.g., using a DSL parser for invariant.rule_expression

        return violations
