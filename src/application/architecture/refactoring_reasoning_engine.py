"""Engine to detect refactoring candidates from architectural code smells."""

import uuid
from datetime import datetime
from typing import List

from .architecture_graph import ArchitectureGraph
from .refactoring_candidate import RefactoringCandidate, RefactoringCandidateType, RefactoringPriority
from .architecture_fitness import ArchitectureFitness

class RefactoringReasoningEngine:
    """Detects code smells and architecture violations from graph metrics."""

    def detect_refactoring_candidates(
        self,
        graph: ArchitectureGraph,
        fitness: ArchitectureFitness
    ) -> List[RefactoringCandidate]:
        """
        Analyzes the architecture graph and fitness scores to identify refactoring opportunities.
        """
        candidates = []
        
        # 1. Detect Cycles
        cycles = graph.detect_cycles()
        if cycles:
            for cycle in cycles:
                candidates.append(RefactoringCandidate(
                    id=uuid.uuid4(),
                    candidate_type=RefactoringCandidateType.CYCLE,
                    priority=RefactoringPriority.CRITICAL if len(cycle) < 3 else RefactoringPriority.HIGH,
                    target_entities=cycle,
                    evidence={"cycle_path": cycle},
                    expected_benefit="Breaks dependency cycle, improving modularity and testability.",
                    fitness_impact=0.15,
                    detected_at=datetime.utcnow()
                ))
                
        # 2. High Coupling / Low Cohesion heuristics
        for node_id, node in graph.nodes.items():
            fan_in = graph.fan_in(node_id)
            fan_out = graph.fan_out(node_id)
            
            # Simple heuristic for GOD_CLASS or BLOB_SERVICE
            if fan_out > 10 and fan_in > 10:
                candidates.append(RefactoringCandidate(
                    id=uuid.uuid4(),
                    candidate_type=RefactoringCandidateType.BLOB_SERVICE if node.node_type == "Service" else RefactoringCandidateType.GOD_CLASS,
                    priority=RefactoringPriority.HIGH,
                    target_entities=[node_id],
                    evidence={"fan_in": fan_in, "fan_out": fan_out},
                    expected_benefit="Splitting responsibility reduces coupling and cognitive load.",
                    fitness_impact=0.1,
                    detected_at=datetime.utcnow()
                ))
                
            # High coupling specifically
            if fan_out > 15:
                candidates.append(RefactoringCandidate(
                    id=uuid.uuid4(),
                    candidate_type=RefactoringCandidateType.HIGH_COUPLING,
                    priority=RefactoringPriority.MEDIUM,
                    target_entities=[node_id],
                    evidence={"fan_out": fan_out},
                    expected_benefit="Extracting interfaces or services will reduce instability.",
                    fitness_impact=0.08,
                    detected_at=datetime.utcnow()
                ))
                
        return candidates
