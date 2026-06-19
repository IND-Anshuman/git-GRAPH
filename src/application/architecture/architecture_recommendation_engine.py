"""Engine to provide structural recommendations for architecture improvements."""

import uuid
from typing import List

from .architecture_recommendation import ArchitectureRecommendation, RecommendationType
from .refactoring_candidate import RefactoringCandidate, RefactoringCandidateType
from .architecture_fitness import ArchitectureFitness

class ArchitectureRecommendationEngine:
    """Uses refactoring candidates and fitness metrics to output actionable recommendations."""

    def generate_recommendations(
        self,
        refactoring_candidates: List[RefactoringCandidate],
        current_fitness: ArchitectureFitness
    ) -> List[ArchitectureRecommendation]:
        """
        Translates detected refactoring candidates into specific architectural
        recommendations.
        """
        recommendations = []
        
        for candidate in refactoring_candidates:
            if candidate.candidate_type == RefactoringCandidateType.CYCLE:
                recommendations.append(ArchitectureRecommendation(
                    id=uuid.uuid4(),
                    recommendation_type=RecommendationType.REMOVE_DEPENDENCY,
                    target_elements=candidate.target_entities,
                    action_description=f"Break the circular dependency between {', '.join(candidate.target_entities)}.",
                    justification="Cycles cause tight coupling and prevent independent deployment.",
                    expected_fitness_delta=candidate.fitness_impact,
                    difficulty="HARD"
                ))
            elif candidate.candidate_type in (RefactoringCandidateType.BLOB_SERVICE, RefactoringCandidateType.GOD_CLASS):
                recommendations.append(ArchitectureRecommendation(
                    id=uuid.uuid4(),
                    recommendation_type=RecommendationType.SPLIT_SERVICE,
                    target_elements=candidate.target_entities,
                    action_description=f"Split {candidate.target_entities[0]} into smaller bounded contexts or microservices.",
                    justification="High fan-in and fan-out indicate this component does too much (violates SRP).",
                    expected_fitness_delta=candidate.fitness_impact,
                    difficulty="HARD"
                ))
            elif candidate.candidate_type == RefactoringCandidateType.HIGH_COUPLING:
                recommendations.append(ArchitectureRecommendation(
                    id=uuid.uuid4(),
                    recommendation_type=RecommendationType.INTRODUCE_INTERFACE,
                    target_elements=candidate.target_entities,
                    action_description=f"Introduce an interface for {candidate.target_entities[0]} dependencies.",
                    justification="High outbound dependencies (fan-out) increase instability.",
                    expected_fitness_delta=candidate.fitness_impact,
                    difficulty="MEDIUM"
                ))
                
        # Heuristics based on overall fitness score even without direct candidates
        if current_fitness.cohesion_score < 0.4:
            recommendations.append(ArchitectureRecommendation(
                id=uuid.uuid4(),
                recommendation_type=RecommendationType.MERGE_CAPABILITIES,
                target_elements=[],
                action_description="Consolidate scattered related capabilities into cohesive modules.",
                justification="Low cohesion implies related logic is spread across the system.",
                expected_fitness_delta=0.1,
                difficulty="MEDIUM"
            ))

        return recommendations
