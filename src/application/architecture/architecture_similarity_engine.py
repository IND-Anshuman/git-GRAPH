"""Engine to compute structural similarity between two architectures."""

import uuid
from datetime import datetime
from typing import Dict, Any

from .architecture_graph import ArchitectureGraph
from .architecture_similarity import ArchitectureSimilarity

class ArchitectureSimilarityEngine:
    """Computes similarity metrics between two repository architectures."""

    def compute_similarity(
        self,
        source_repository_id: str,
        target_repository_id: str,
        source_graph: ArchitectureGraph,
        target_graph: ArchitectureGraph
    ) -> ArchitectureSimilarity:
        """
        Computes the similarity between two architecture graphs.
        Uses graph topology, dependency structures, capabilities, and flows.
        """
        
        topology_sim = self._compute_topology_similarity(source_graph, target_graph)
        dependency_sim = self._compute_dependency_similarity(source_graph, target_graph)
        capability_sim = self._compute_capability_similarity(source_graph, target_graph)
        flow_sim = self._compute_flow_similarity(source_graph, target_graph)
        
        # Weighted average or simple average for overall similarity
        weights = {
            "topology": 0.4,
            "dependency": 0.3,
            "capability": 0.2,
            "flow": 0.1
        }
        
        similarity_score = (
            topology_sim * weights["topology"] +
            dependency_sim * weights["dependency"] +
            capability_sim * weights["capability"] +
            flow_sim * weights["flow"]
        )
        
        return ArchitectureSimilarity(
            id=uuid.uuid4(),
            source_repository_id=source_repository_id,
            target_repository_id=target_repository_id,
            similarity_score=similarity_score,
            topology_similarity=topology_sim,
            dependency_similarity=dependency_sim,
            capability_similarity=capability_sim,
            flow_similarity=flow_sim,
            computed_at=datetime.utcnow()
        )
        
    def _compute_topology_similarity(self, g1: ArchitectureGraph, g2: ArchitectureGraph) -> float:
        """Computes structural similarity based on node counts, density, etc."""
        if not g1.nodes and not g2.nodes:
            return 1.0
        if not g1.nodes or not g2.nodes:
            return 0.0
            
        n1, n2 = len(g1.nodes), len(g2.nodes)
        ratio = min(n1, n2) / max(n1, n2)
        
        return min(1.0, max(0.0, ratio))

    def _compute_dependency_similarity(self, g1: ArchitectureGraph, g2: ArchitectureGraph) -> float:
        """Computes dependency structure similarity."""
        if not g1.edges and not g2.edges:
            return 1.0
        if not g1.edges or not g2.edges:
            return 0.0
            
        e1, e2 = len(g1.edges), len(g2.edges)
        ratio = min(e1, e2) / max(e1, e2)
        
        return min(1.0, max(0.0, ratio))
        
    def _compute_capability_similarity(self, g1: ArchitectureGraph, g2: ArchitectureGraph) -> float:
        """Computes similarity of architectural capabilities provided."""
        # Simulated logic for capabilities
        return 0.5
        
    def _compute_flow_similarity(self, g1: ArchitectureGraph, g2: ArchitectureGraph) -> float:
        """Computes similarity of typical flows (e.g. data flows, execution paths)."""
        # Simulated logic for flow
        return 0.5
