"""Engine for computing architecture fitness metrics."""

from typing import Dict, Any, List, Set
from .architecture_graph import ArchitectureGraph
from .architecture_fitness import ArchitectureFitness


class FitnessFunctionEngine:
    """Computes architecture fitness metrics from graph topology."""

    def compute_fitness(self, graph: ArchitectureGraph) -> ArchitectureFitness:
        """
        Calculate fitness metrics for a given architecture graph.
        
        All metrics return a float between 0.0 and 1.0.
        """
        nodes = graph.nodes
        edges = graph.edges
        total_nodes = len(nodes)
        total_edges = len(edges)
        
        if total_nodes == 0:
            return ArchitectureFitness(
                coupling_score=1.0,
                cohesion_score=1.0,
                instability_score=0.0,
                abstractness_score=0.0,
                distance_from_main_sequence=1.0,
                cyclicity_score=0.0,
                layer_violation_score=0.0,
                overall_score=1.0,
                formulas={"info": "Empty graph"}
            )

        # Coupling: 1.0 = highly decoupled, 0.0 = highly coupled
        # Heuristic: max possible edges is N * (N-1)
        max_possible_edges = total_nodes * (total_nodes - 1)
        if max_possible_edges > 0:
            edge_density = total_edges / max_possible_edges
            coupling_score = max(0.0, 1.0 - edge_density)
        else:
            coupling_score = 1.0

        # Cohesion: simplistic heuristic (internal edges vs external edges, or just placeholder)
        # We assume 0.5 as base, maybe adjust based on connected components
        cohesion_score = 0.5

        # Instability: Ce / (Ca + Ce)
        # Ce = efferent coupling (fan-out), Ca = afferent coupling (fan-in)
        total_fan_out = sum(graph.fan_out(node_id) for node_id in nodes)
        total_fan_in = sum(graph.fan_in(node_id) for node_id in nodes)
        total_coupling = total_fan_out + total_fan_in
        if total_coupling > 0:
            instability_score = total_fan_out / total_coupling
        else:
            instability_score = 0.0

        # Abstractness: abstract / total types
        abstractness_score = 0.0 # Placeholder for now

        # Distance from main sequence: |A + I - 1|
        # Ideally, Distance from Main Sequence = |Abstractness + Instability - 1|
        # In range [0, 1]. D=0 is best (on the line), D=1 is worst.
        distance_from_main_sequence = abs(abstractness_score + instability_score - 1.0)
        
        # We typically want distance_score where 1.0 is best and 0.0 is worst?
        # But ArchitectureFitness definition implies it's just the value |A + I - 1|.
        # Actually, |A+I-1| is usually [0,1], 0 is good, 1 is bad.
        # But the class comment says "All scores are in [0.0, 1.0]" meaning 1.0 is usually best?
        # Let's keep it as the distance value itself.

        # Cyclicity: fraction of nodes in cycles
        cycles = graph.detect_cycles()
        nodes_in_cycles: Set[str] = set()
        for cycle in cycles:
            nodes_in_cycles.update(cycle)
        cyclicity_score = len(nodes_in_cycles) / total_nodes

        # Layer violation score: violations / total edges
        # Just passing an empty layer order for now, or maybe not computable without one.
        layer_violation_score = 0.0
        
        # Overall score
        # Let's say we want higher to be better.
        # coupling_score (higher better), cohesion (higher better)
        # instability (depends, let's say average)
        # cyclicity (lower better) -> 1 - cyclicity
        # layer_violation (lower better) -> 1 - layer_violation
        overall = (coupling_score + cohesion_score + (1.0 - cyclicity_score) + (1.0 - layer_violation_score)) / 4.0

        formulas = {
            "coupling": "1.0 - (E / (N * (N - 1)))",
            "cohesion": "Placeholder heuristic",
            "instability": "Ce / (Ca + Ce)",
            "abstractness": "Abstract / Total",
            "distance_from_main_sequence": "|A + I - 1|",
            "cyclicity": "Nodes in cycles / Total nodes",
            "layer_violation": "Violations / E",
            "overall": "Average of normalized scores"
        }

        return ArchitectureFitness(
            coupling_score=coupling_score,
            cohesion_score=cohesion_score,
            instability_score=instability_score,
            abstractness_score=abstractness_score,
            distance_from_main_sequence=distance_from_main_sequence,
            cyclicity_score=cyclicity_score,
            layer_violation_score=layer_violation_score,
            overall_score=overall,
            formulas=formulas
        )
