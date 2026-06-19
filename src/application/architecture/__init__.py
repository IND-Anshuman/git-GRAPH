"""
Phase 7B Architectural Intelligence Layer (AIL)

This package contains the domain models, engines, and strategies for detecting,
validating, scoring, and reasoning about software architecture from graph evidence.
"""

from .architecture_type import ArchitectureType
from .architecture_confidence import ArchitectureConfidence
from .architecture_evidence import ArchitectureEvidence
from .architecture_profile import ArchitectureProfile
from .architecture_snapshot import ArchitectureSnapshot
from .architecture_violation import ArchitectureViolation, ViolationSeverity
from .architecture_invariant import ArchitectureInvariant
from .architecture_fitness import ArchitectureFitness
from .architecture_drift import ArchitectureDrift, ArchitectureDriftType
from .architecture_timeline import ArchitectureTimeline, ArchitectureTimelineEntry
from .architecture_benchmark import ArchitectureBenchmark
from .architecture_similarity import ArchitectureSimilarity
from .ownership_profile import OwnershipProfile
from .refactoring_candidate import RefactoringCandidate, RefactoringCandidateType, RefactoringPriority
from .architecture_recommendation import ArchitectureRecommendation, RecommendationType
from .architecture_graph import ArchitectureGraph, ArchitectureNode, ArchitectureEdge
from .fitness_function_engine import FitnessFunctionEngine
from .bounded_context_engine import BoundedContextEngine
from .architecture_reasoning_engine import ArchitectureReasoningEngine
from .invariant_reasoning_engine import InvariantReasoningEngine
from .architecture_similarity_engine import ArchitectureSimilarityEngine
from .architecture_benchmark_engine import ArchitectureBenchmarkEngine
from .drift_reasoning_engine import DriftReasoningEngine
from .architecture_timeline_engine import ArchitectureTimelineEngine
from .ownership_reasoning_engine import OwnershipReasoningEngine
from .refactoring_reasoning_engine import RefactoringReasoningEngine
from .architecture_recommendation_engine import ArchitectureRecommendationEngine
__all__ = [
    "ArchitectureType",
    "ArchitectureConfidence",
    "ArchitectureEvidence",
    "ArchitectureProfile",
    "ArchitectureSnapshot",
    "ArchitectureViolation",
    "ViolationSeverity",
    "ArchitectureInvariant",
    "ArchitectureFitness",
    "ArchitectureDrift",
    "ArchitectureDriftType",
    "ArchitectureTimeline",
    "ArchitectureTimelineEntry",
    "ArchitectureBenchmark",
    "ArchitectureSimilarity",
    "OwnershipProfile",
    "RefactoringCandidate",
    "RefactoringCandidateType",
    "RefactoringPriority",
    "ArchitectureRecommendation",
    "RecommendationType",
    "ArchitectureGraph",
    "ArchitectureNode",
    "ArchitectureEdge",
    "FitnessFunctionEngine",
    "BoundedContextEngine",
    "ArchitectureReasoningEngine",
    "InvariantReasoningEngine",
    "ArchitectureSimilarityEngine",
    "ArchitectureBenchmarkEngine",
    "DriftReasoningEngine",
    "ArchitectureTimelineEngine",
    "OwnershipReasoningEngine",
    "RefactoringReasoningEngine",
    "ArchitectureRecommendationEngine",]
