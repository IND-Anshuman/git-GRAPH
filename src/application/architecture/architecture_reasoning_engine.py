"""Reasoning engine to detect architecture styles from the graph."""

import uuid
from datetime import datetime
from typing import Dict, Any, List

from .architecture_graph import ArchitectureGraph
from .architecture_pattern_registry import ArchitecturePatternRegistry
from .architecture_profile import ArchitectureProfile
from .architecture_type import ArchitectureType
from .architecture_confidence import ArchitectureConfidence
from .architecture_evidence import ArchitectureEvidence

class ArchitectureReasoningEngine:
    """Uses topology signatures to detect architecture styles from a graph."""

    def __init__(self, pattern_registry: ArchitecturePatternRegistry) -> None:
        """Initialize with a pattern registry."""
        self.pattern_registry = pattern_registry

    def detect_architecture(
        self,
        repository_id: str,
        commit_hash: str,
        graph: ArchitectureGraph
    ) -> ArchitectureProfile:
        """
        Detects the architecture style for the given repository and commit using
        the provided graph and loaded patterns.
        """
        best_match_type = ArchitectureType.UNKNOWN
        best_match_score = 0.0
        best_confidence: ArchitectureConfidence | None = None
        best_evidence: ArchitectureEvidence | None = None
        
        all_patterns = self.pattern_registry.get_all_patterns()

        for pattern_name, pattern_data in all_patterns.items():
            # Evaluate each pattern against the graph
            # This is a heuristic mock implementation for demonstration.
            # In reality, this would evaluate topology constraints.
            
            # Simulated matching based on graph features
            topology_match = self._evaluate_topology(graph, pattern_data)
            dependency_match = self._evaluate_dependencies(graph, pattern_data)
            
            # Assume 0.5 for others unless more data is provided
            confidence = ArchitectureConfidence.compute(
                topology_match=topology_match,
                dependency_match=dependency_match,
                flow_match=0.5,
                capability_match=0.5,
                ownership_match=0.5,
                historical_match=0.5,
                evidence_coverage=0.5
            )
            
            if confidence.score > best_match_score:
                best_match_score = confidence.score
                # Try to map pattern name to enum, default to UNKNOWN
                try:
                    best_match_type = ArchitectureType[pattern_name.upper()]
                except KeyError:
                    best_match_type = ArchitectureType.UNKNOWN
                
                best_confidence = confidence
                
                best_evidence = ArchitectureEvidence(
                    supporting_patterns=[pattern_name] if topology_match > 0.5 else [],
                    violating_patterns=[]
                )

        if not best_confidence:
            best_confidence = ArchitectureConfidence.compute(
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            )
            best_evidence = ArchitectureEvidence()

        return ArchitectureProfile(
            id=uuid.uuid4(),
            architecture_type=best_match_type,
            confidence=best_confidence,
            description=f"Detected {best_match_type.value} architecture.",
            evidence=best_evidence,
            detected_at=datetime.utcnow(),
            repository_id=repository_id,
            commit_hash=commit_hash
        )

    def _evaluate_topology(self, graph: ArchitectureGraph, pattern_data: Dict[str, Any]) -> float:
        """Heuristic evaluation of graph topology against pattern rules."""
        if not graph.nodes:
            return 0.0
        # Placeholder logic: return 0.6 to simulate partial match
        return 0.6

    def _evaluate_dependencies(self, graph: ArchitectureGraph, pattern_data: Dict[str, Any]) -> float:
        """Heuristic evaluation of graph dependencies against pattern rules."""
        if not graph.edges:
            return 0.0
        # Placeholder logic: return 0.7 to simulate partial match
        return 0.7
