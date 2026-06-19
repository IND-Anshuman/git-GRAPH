"""Engine to benchmark an architecture against a group of peers."""

import uuid
from datetime import datetime
from typing import List

from .architecture_benchmark import ArchitectureBenchmark
from .architecture_fitness import ArchitectureFitness

class ArchitectureBenchmarkEngine:
    """Compares current architecture fitness against peer repositories."""

    def compute_benchmark(
        self,
        repository_id: str,
        commit_hash: str,
        current_fitness: ArchitectureFitness,
        peer_group_name: str,
        peer_fitness_scores: List[float]
    ) -> ArchitectureBenchmark:
        """
        Benchmarks the given fitness against a provided list of peer fitness scores.
        """
        if not peer_fitness_scores:
            return ArchitectureBenchmark(
                id=uuid.uuid4(),
                repository_id=repository_id,
                commit_hash=commit_hash,
                current_fitness=current_fitness.overall_score,
                comparison_group=peer_group_name,
                comparison_avg_fitness=current_fitness.overall_score,
                percentile_rank=1.0,
                key_gaps=[],
                generated_at=datetime.utcnow()
            )
            
        avg_fitness = sum(peer_fitness_scores) / len(peer_fitness_scores)
        
        # Calculate percentile rank
        lower_scores = [score for score in peer_fitness_scores if score < current_fitness.overall_score]
        percentile = len(lower_scores) / len(peer_fitness_scores)
        
        # Determine key gaps deterministically based on fitness details
        gaps = []
        if current_fitness.coupling_score < 0.5:
            gaps.append("High Coupling")
        if current_fitness.cohesion_score < 0.5:
            gaps.append("Low Cohesion")
        if current_fitness.cyclicity_score > 0.2:
            gaps.append("High Cyclicity")
            
        return ArchitectureBenchmark(
            id=uuid.uuid4(),
            repository_id=repository_id,
            commit_hash=commit_hash,
            current_fitness=current_fitness.overall_score,
            comparison_group=peer_group_name,
            comparison_avg_fitness=avg_fitness,
            percentile_rank=percentile,
            key_gaps=gaps,
            generated_at=datetime.utcnow()
        )
