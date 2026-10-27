"""
Phase 7B Architectural Intelligence Layer (AIL)

This package contains the domain models, engines, and strategies for detecting,
validating, scoring, and reasoning about software architecture from graph evidence.
"""

from .architecture_benchmark import ArchitectureBenchmark
from .architecture_benchmark_engine import ArchitectureBenchmarkEngine
from .architecture_confidence import ArchitectureConfidence
from .architecture_drift import ArchitectureDrift, ArchitectureDriftType
from .architecture_evidence import ArchitectureEvidence
from .architecture_fitness import ArchitectureFitness
from .architecture_graph import ArchitectureEdge, ArchitectureGraph, ArchitectureNode
from .architecture_invariant import ArchitectureInvariant
from .architecture_profile import ArchitectureProfile
from .architecture_reasoning_engine import ArchitectureReasoningEngine
from .architecture_recommendation import ArchitectureRecommendation, RecommendationType
from .architecture_recommendation_engine import ArchitectureRecommendationEngine
from .architecture_similarity import ArchitectureSimilarity
from .architecture_similarity_engine import ArchitectureSimilarityEngine
from .architecture_snapshot import ArchitectureSnapshot
from .architecture_timeline import ArchitectureTimeline, ArchitectureTimelineEntry
from .architecture_timeline_engine import ArchitectureTimelineEngine
from .architecture_type import ArchitectureType
from .architecture_violation import ArchitectureViolation, ViolationSeverity
from .bounded_context_engine import BoundedContextEngine
from .drift_reasoning_engine import DriftReasoningEngine
from .fitness_function_engine import FitnessFunctionEngine
from .invariant_reasoning_engine import InvariantReasoningEngine
from .ownership_profile import OwnershipProfile
from .ownership_reasoning_engine import OwnershipReasoningEngine
from .refactoring_candidate import RefactoringCandidate, RefactoringCandidateType, RefactoringPriority
from .refactoring_reasoning_engine import RefactoringReasoningEngine

__all__ = [
    "ArchitectureBenchmark",
    "ArchitectureBenchmarkEngine",
    "ArchitectureConfidence",
    "ArchitectureDrift",
    "ArchitectureDriftType",
    "ArchitectureEdge",
    "ArchitectureEvidence",
    "ArchitectureFitness",
    "ArchitectureGraph",
    "ArchitectureInvariant",
    "ArchitectureNode",
    "ArchitectureProfile",
    "ArchitectureReasoningEngine",
    "ArchitectureRecommendation",
    "ArchitectureRecommendationEngine",
    "ArchitectureSimilarity",
    "ArchitectureSimilarityEngine",
    "ArchitectureSnapshot",
    "ArchitectureTimeline",
    "ArchitectureTimelineEngine",
    "ArchitectureTimelineEntry",
    "ArchitectureType",
    "ArchitectureViolation",
    "BoundedContextEngine",
    "DriftReasoningEngine",
    "FitnessFunctionEngine",
    "InvariantReasoningEngine",
    "OwnershipProfile",
    "OwnershipReasoningEngine",
    "RecommendationType",
    "RefactoringCandidate",
    "RefactoringCandidateType",
    "RefactoringPriority",
    "RefactoringReasoningEngine",
    "ViolationSeverity",
]
