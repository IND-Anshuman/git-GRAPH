from fastapi import Request
from typing import Callable, Any
from src.application.use_cases.ingest_repository import IngestRepositoryUseCase
from src.application.use_cases.get_repository import GetRepositoryUseCase
from src.application.use_cases.delete_repository import DeleteRepositoryUseCase
from src.application.use_cases.query_entities import QueryEntitiesUseCase
from src.application.use_cases.query_relationships import QueryRelationshipsUseCase
from src.application.use_cases.scan_repository_history import ScanRepositoryHistoryUseCase
from src.application.use_cases.get_commits import GetCommitsUseCase
from src.application.use_cases.get_entity_history import GetEntityHistoryUseCase
from src.application.use_cases.get_commit_changes import GetCommitChangesUseCase
from src.application.use_cases.get_repository_timeline import GetRepositoryTimelineUseCase
from src.application.use_cases.reconstruct_graph import ReconstructGraphUseCase

# Phase 3 Use Cases
from src.application.use_cases.extract_logic_use_case import ExtractLogicUseCase
from src.application.use_cases.extract_all_logic_use_case import ExtractAllLogicUseCase
from src.application.use_cases.get_logic_timeline_use_case import GetLogicTimelineUseCase
from src.application.use_cases.get_entity_logic_use_case import GetEntityLogicUseCase
from src.application.use_cases.get_entity_logic_history_use_case import GetEntityLogicHistoryUseCase
from src.application.use_cases.get_behavior_evolution_use_case import GetBehaviorEvolutionUseCase
from src.application.use_cases.get_logic_evidence_use_case import GetLogicEvidenceUseCase
from src.application.use_cases.get_behavior_explanation_use_case import GetBehaviorExplanationUseCase
from src.application.use_cases.get_behavior_drift_use_case import GetBehaviorDriftUseCase
from src.application.use_cases.validate_logic_use_case import ValidateLogicUseCase

# Phase 4 Use Cases
from src.application.use_cases.detect_concepts import DetectConceptsUseCase
from src.application.use_cases.get_concepts import GetConceptsUseCase
from src.application.use_cases.get_concept_evolution import GetConceptEvolutionUseCase
from src.application.use_cases.get_concept_relationships import GetConceptRelationshipsUseCase
from src.application.use_cases.get_concept_drift import GetConceptDriftUseCase
from src.application.use_cases.get_concept_explanation import GetConceptExplanationUseCase
from src.application.services.concept_backfill_service import ConceptBackfillService
from src.application.use_cases.extract_all_in_one_concepts_use_case import ExtractAllInOneConceptsUseCase


def get_container(request: Request) -> Any:
    return request.app.state.container

def get_uow_factory(request: Request) -> Callable:
    return request.app.state.container.get_uow_factory()

def get_uow(request: Request) -> Any:
    return request.app.state.container.get_uow_factory()()

def get_ingest_use_case(request: Request) -> IngestRepositoryUseCase:
    return request.app.state.container.get_ingest_repository_use_case()

def get_get_repository_use_case(request: Request) -> GetRepositoryUseCase:
    return request.app.state.container.get_get_repository_use_case()

def get_query_entities_use_case(request: Request) -> QueryEntitiesUseCase:
    return request.app.state.container.get_query_entities_use_case()

def get_query_relationships_use_case(request: Request) -> QueryRelationshipsUseCase:
    return request.app.state.container.get_query_relationships_use_case()

def get_scan_history_use_case(request: Request) -> ScanRepositoryHistoryUseCase:
    return request.app.state.container.get_scan_repository_history_use_case()

def get_get_commits_use_case(request: Request) -> GetCommitsUseCase:
    return request.app.state.container.get_get_commits_use_case()

def get_entity_history_use_case(request: Request) -> GetEntityHistoryUseCase:
    return request.app.state.container.get_entity_history_use_case()

def get_commit_changes_use_case(request: Request) -> GetCommitChangesUseCase:
    return request.app.state.container.get_commit_changes_use_case()

def get_repository_timeline_use_case(request: Request) -> GetRepositoryTimelineUseCase:
    return request.app.state.container.get_repository_timeline_use_case()

def get_reconstruct_graph_use_case(request: Request) -> ReconstructGraphUseCase:
    return request.app.state.container.get_reconstruct_graph_use_case()

def get_health_score_engine(request: Request) -> Any:
    return request.app.state.container.health_score_engine

def get_temporal_integrity_service(request: Request) -> Any:
    return request.app.state.container.temporal_integrity_service

def get_temporal_explorer(request: Request) -> Any:
    return request.app.state.container.temporal_explorer

def get_temporal_replay_service(request: Request) -> Any:
    return request.app.state.container.temporal_replay_service

def get_extract_logic_use_case(request: Request) -> ExtractLogicUseCase:
    return request.app.state.container.get_extract_logic_use_case()

def get_extract_all_logic_use_case(request: Request) -> ExtractAllLogicUseCase:
    return request.app.state.container.get_extract_all_logic_use_case()

def get_get_logic_timeline_use_case(request: Request) -> GetLogicTimelineUseCase:
    return request.app.state.container.get_get_logic_timeline_use_case()

def get_get_entity_logic_use_case(request: Request) -> GetEntityLogicUseCase:
    return request.app.state.container.get_get_entity_logic_use_case()

def get_get_entity_logic_history_use_case(request: Request) -> GetEntityLogicHistoryUseCase:
    return request.app.state.container.get_get_entity_logic_history_use_case()

def get_get_behavior_evolution_use_case(request: Request) -> GetBehaviorEvolutionUseCase:
    return request.app.state.container.get_get_behavior_evolution_use_case()

def get_get_logic_evidence_use_case(request: Request) -> GetLogicEvidenceUseCase:
    return request.app.state.container.get_get_logic_evidence_use_case()

def get_get_behavior_explanation_use_case(request: Request) -> GetBehaviorExplanationUseCase:
    return request.app.state.container.get_get_behavior_explanation_use_case()

def get_get_behavior_drift_use_case(request: Request) -> GetBehaviorDriftUseCase:
    return request.app.state.container.get_get_behavior_drift_use_case()

def get_validate_logic_use_case(request: Request) -> ValidateLogicUseCase:
    return request.app.state.container.get_validate_logic_use_case()

def get_delete_repository_use_case(request: Request) -> DeleteRepositoryUseCase:
    return request.app.state.container.get_delete_repository_use_case()

def get_detect_concepts_use_case(request: Request) -> DetectConceptsUseCase:
    return request.app.state.container.get_detect_concepts_use_case()

def get_get_concepts_use_case(request: Request) -> GetConceptsUseCase:
    return request.app.state.container.get_get_concepts_use_case()

def get_get_concept_evolution_use_case(request: Request) -> GetConceptEvolutionUseCase:
    return request.app.state.container.get_get_concept_evolution_use_case()

def get_get_concept_relationships_use_case(request: Request) -> GetConceptRelationshipsUseCase:
    return request.app.state.container.get_get_concept_relationships_use_case()

def get_get_concept_drift_use_case(request: Request) -> GetConceptDriftUseCase:
    return request.app.state.container.get_get_concept_drift_use_case()

def get_get_concept_explanation_use_case(request: Request) -> GetConceptExplanationUseCase:
    return request.app.state.container.get_get_concept_explanation_use_case()

def get_concept_backfill_service(request: Request) -> ConceptBackfillService:
    return request.app.state.container.get_concept_backfill_service()

def get_extract_all_in_one_concepts_use_case(request: Request) -> ExtractAllInOneConceptsUseCase:
    return request.app.state.container.get_extract_all_in_one_concepts_use_case()


# Phase 4.5 Semantic Expansion Bounded Context
from src.application.semantic.behavior_registry.canonical_registry import CanonicalRegistry
from src.application.semantic.type_resolution.type_resolution_engine import TypeResolutionEngine
from src.application.semantic.normalization.semantic_normalizer import SemanticNormalizer

def get_canonical_registry(request: Request) -> CanonicalRegistry:
    return request.app.state.container.get_canonical_registry()

def get_type_resolution_engine(request: Request) -> TypeResolutionEngine:
    return request.app.state.container.get_type_resolution_engine()

def get_semantic_normalizer(request: Request) -> SemanticNormalizer:
    return request.app.state.container.get_semantic_normalizer()


# Phase 5A Discovery / Meta-Ontology Bounded Context
from src.application.semantic.embedding.embedding_registry import EmbeddingRegistry
from src.application.semantic.calibration.calibration_engine import ConfidenceCalibrationEngine
from src.application.semantic.schema.schema_registry import SchemaRegistry
from src.application.semantic.governance.governance_manager import GovernanceManager
from src.application.semantic.discovery import (
    EntityDiscoveryEngine,
    RelationshipDiscoveryEngine,
    BehaviorDiscoveryEngine,
    ConceptDiscoveryEngine,
    FlowDiscoveryEngine,
)
from src.application.semantic.evolution import SemanticEvolutionEngine

def get_embedding_registry(request: Request) -> EmbeddingRegistry:
    return request.app.state.container.get_embedding_registry()

def get_calibration_engine(request: Request) -> ConfidenceCalibrationEngine:
    return request.app.state.container.get_calibration_engine()

def get_schema_registry(request: Request) -> SchemaRegistry:
    return request.app.state.container.get_schema_registry()

def get_governance_manager(request: Request) -> GovernanceManager:
    return request.app.state.container.get_governance_manager()

def get_entity_discovery_engine(request: Request) -> EntityDiscoveryEngine:
    return request.app.state.container.get_entity_discovery_engine()

def get_relationship_discovery_engine(request: Request) -> RelationshipDiscoveryEngine:
    return request.app.state.container.get_relationship_discovery_engine()

def get_behavior_discovery_engine(request: Request) -> BehaviorDiscoveryEngine:
    return request.app.state.container.get_behavior_discovery_engine()

def get_concept_discovery_engine(request: Request) -> ConceptDiscoveryEngine:
    return request.app.state.container.get_concept_discovery_engine()

def get_flow_discovery_engine(request: Request) -> FlowDiscoveryEngine:
    return request.app.state.container.get_flow_discovery_engine()

def get_semantic_evolution_engine(request: Request) -> SemanticEvolutionEngine:
    return request.app.state.container.get_semantic_evolution_engine()


# Phase 6 Capability Intelligence Layer
from src.application.capabilities import (
    CapabilityDiscoveryEngine,
    CapabilityConfidenceEngine,
    CapabilityOverlapEngine,
    CapabilityStabilityEngine,
    CapabilityOwnershipEngine,
    CapabilityDriftEngine,
    CapabilityRiskEngine,
    CapabilityPlacementEngine,
    CapabilityGovernanceEngine,
    CapabilityEvolutionEngine,
    CapabilityDependencyGraph,
    CapabilityHealthEngine,
    BlastRadiusEngine,
    CapabilityQueryEngine,
    CapabilitySummary,
    CapabilityBoundaryEngine,
    CapabilityCohesionEngine,
    CapabilityCouplingEngine,
    TaxonomyLearningEngine,
    CapabilityEmbedding,
)

def get_capability_discovery_engine(request: Request) -> CapabilityDiscoveryEngine:
    return request.app.state.container.get_capability_discovery_engine()

def get_capability_confidence_engine(request: Request) -> CapabilityConfidenceEngine:
    return request.app.state.container.get_capability_confidence_engine()

def get_capability_overlap_engine(request: Request) -> CapabilityOverlapEngine:
    return request.app.state.container.get_capability_overlap_engine()

def get_capability_stability_engine(request: Request) -> CapabilityStabilityEngine:
    return request.app.state.container.get_capability_stability_engine()

def get_capability_ownership_engine(request: Request) -> CapabilityOwnershipEngine:
    return request.app.state.container.get_capability_ownership_engine()

def get_capability_drift_engine(request: Request) -> CapabilityDriftEngine:
    return request.app.state.container.get_capability_drift_engine()

def get_capability_risk_engine(request: Request) -> CapabilityRiskEngine:
    return request.app.state.container.get_capability_risk_engine()

def get_capability_placement_engine(request: Request) -> CapabilityPlacementEngine:
    return request.app.state.container.get_capability_placement_engine()

def get_capability_governance_engine(request: Request) -> CapabilityGovernanceEngine:
    return request.app.state.container.get_capability_governance_engine()

def get_capability_evolution_engine(request: Request) -> CapabilityEvolutionEngine:
    return request.app.state.container.get_capability_evolution_engine()

def get_capability_dependency_graph(request: Request) -> CapabilityDependencyGraph:
    return request.app.state.container.get_capability_dependency_graph()

def get_capability_health_engine(request: Request) -> CapabilityHealthEngine:
    return request.app.state.container.get_capability_health_engine()

def get_blast_radius_engine(request: Request) -> BlastRadiusEngine:
    return request.app.state.container.get_blast_radius_engine()

def get_capability_query_engine(request: Request) -> CapabilityQueryEngine:
    return request.app.state.container.get_capability_query_engine()

def get_capability_summary(request: Request) -> CapabilitySummary:
    return request.app.state.container.get_capability_summary()

def get_capability_boundary_engine(request: Request) -> CapabilityBoundaryEngine:
    return request.app.state.container.get_capability_boundary_engine()

def get_capability_cohesion_engine(request: Request) -> CapabilityCohesionEngine:
    return request.app.state.container.get_capability_cohesion_engine()

def get_capability_coupling_engine(request: Request) -> CapabilityCouplingEngine:
    return request.app.state.container.get_capability_coupling_engine()

def get_taxonomy_learning_engine(request: Request) -> TaxonomyLearningEngine:
    return request.app.state.container.get_taxonomy_learning_engine()

def get_capability_embedding(request: Request) -> CapabilityEmbedding:
    return request.app.state.container.get_capability_embedding()


# Phase 7A Reasoning Intelligence Layer
from src.application.reasoning.reasoning_query_engine import ReasoningQueryEngine
from src.application.reasoning.reasoning_cache import ReasoningCache
from src.application.reasoning.reasoning_strategy_registry import ReasoningStrategyRegistry


def get_reasoning_query_engine(request: Request) -> ReasoningQueryEngine:
    return request.app.state.container.get_reasoning_query_engine()

def get_get_behavior_evolution_use_case(request: Request) -> GetBehaviorEvolutionUseCase:
    return request.app.state.container.get_get_behavior_evolution_use_case()

def get_get_logic_evidence_use_case(request: Request) -> GetLogicEvidenceUseCase:
    return request.app.state.container.get_get_logic_evidence_use_case()

def get_get_behavior_explanation_use_case(request: Request) -> GetBehaviorExplanationUseCase:
    return request.app.state.container.get_get_behavior_explanation_use_case()

def get_get_behavior_drift_use_case(request: Request) -> GetBehaviorDriftUseCase:
    return request.app.state.container.get_get_behavior_drift_use_case()

def get_validate_logic_use_case(request: Request) -> ValidateLogicUseCase:
    return request.app.state.container.get_validate_logic_use_case()

def get_delete_repository_use_case(request: Request) -> DeleteRepositoryUseCase:
    return request.app.state.container.get_delete_repository_use_case()

def get_detect_concepts_use_case(request: Request) -> DetectConceptsUseCase:
    return request.app.state.container.get_detect_concepts_use_case()

def get_get_concepts_use_case(request: Request) -> GetConceptsUseCase:
    return request.app.state.container.get_get_concepts_use_case()

def get_get_concept_evolution_use_case(request: Request) -> GetConceptEvolutionUseCase:
    return request.app.state.container.get_get_concept_evolution_use_case()

def get_get_concept_relationships_use_case(request: Request) -> GetConceptRelationshipsUseCase:
    return request.app.state.container.get_get_concept_relationships_use_case()

def get_get_concept_drift_use_case(request: Request) -> GetConceptDriftUseCase:
    return request.app.state.container.get_get_concept_drift_use_case()

def get_get_concept_explanation_use_case(request: Request) -> GetConceptExplanationUseCase:
    return request.app.state.container.get_get_concept_explanation_use_case()

def get_concept_backfill_service(request: Request) -> ConceptBackfillService:
    return request.app.state.container.get_concept_backfill_service()


# Phase 4.5 Semantic Expansion Bounded Context
from src.application.semantic.behavior_registry.canonical_registry import CanonicalRegistry
from src.application.semantic.type_resolution.type_resolution_engine import TypeResolutionEngine
from src.application.semantic.normalization.semantic_normalizer import SemanticNormalizer

def get_canonical_registry(request: Request) -> CanonicalRegistry:
    return request.app.state.container.get_canonical_registry()

def get_type_resolution_engine(request: Request) -> TypeResolutionEngine:
    return request.app.state.container.get_type_resolution_engine()

def get_semantic_normalizer(request: Request) -> SemanticNormalizer:
    return request.app.state.container.get_semantic_normalizer()


# Phase 5A Discovery / Meta-Ontology Bounded Context
from src.application.semantic.embedding.embedding_registry import EmbeddingRegistry
from src.application.semantic.calibration.calibration_engine import ConfidenceCalibrationEngine
from src.application.semantic.schema.schema_registry import SchemaRegistry
from src.application.semantic.governance.governance_manager import GovernanceManager
from src.application.semantic.discovery import (
    EntityDiscoveryEngine,
    RelationshipDiscoveryEngine,
    BehaviorDiscoveryEngine,
    ConceptDiscoveryEngine,
    FlowDiscoveryEngine,
)
from src.application.semantic.evolution import SemanticEvolutionEngine

def get_embedding_registry(request: Request) -> EmbeddingRegistry:
    return request.app.state.container.get_embedding_registry()

def get_calibration_engine(request: Request) -> ConfidenceCalibrationEngine:
    return request.app.state.container.get_calibration_engine()

def get_schema_registry(request: Request) -> SchemaRegistry:
    return request.app.state.container.get_schema_registry()

def get_governance_manager(request: Request) -> GovernanceManager:
    return request.app.state.container.get_governance_manager()

def get_entity_discovery_engine(request: Request) -> EntityDiscoveryEngine:
    return request.app.state.container.get_entity_discovery_engine()

def get_relationship_discovery_engine(request: Request) -> RelationshipDiscoveryEngine:
    return request.app.state.container.get_relationship_discovery_engine()

def get_behavior_discovery_engine(request: Request) -> BehaviorDiscoveryEngine:
    return request.app.state.container.get_behavior_discovery_engine()

def get_concept_discovery_engine(request: Request) -> ConceptDiscoveryEngine:
    return request.app.state.container.get_concept_discovery_engine()

def get_flow_discovery_engine(request: Request) -> FlowDiscoveryEngine:
    return request.app.state.container.get_flow_discovery_engine()

def get_semantic_evolution_engine(request: Request) -> SemanticEvolutionEngine:
    return request.app.state.container.get_semantic_evolution_engine()


# Phase 6 Capability Intelligence Layer
from src.application.capabilities import (
    CapabilityDiscoveryEngine,
    CapabilityConfidenceEngine,
    CapabilityOverlapEngine,
    CapabilityStabilityEngine,
    CapabilityOwnershipEngine,
    CapabilityDriftEngine,
    CapabilityRiskEngine,
    CapabilityPlacementEngine,
    CapabilityGovernanceEngine,
    CapabilityEvolutionEngine,
    CapabilityDependencyGraph,
    CapabilityHealthEngine,
    BlastRadiusEngine,
    CapabilityQueryEngine,
    CapabilitySummary,
    CapabilityBoundaryEngine,
    CapabilityCohesionEngine,
    CapabilityCouplingEngine,
    TaxonomyLearningEngine,
    CapabilityEmbedding,
)

def get_capability_discovery_engine(request: Request) -> CapabilityDiscoveryEngine:
    return request.app.state.container.get_capability_discovery_engine()

def get_capability_confidence_engine(request: Request) -> CapabilityConfidenceEngine:
    return request.app.state.container.get_capability_confidence_engine()

def get_capability_overlap_engine(request: Request) -> CapabilityOverlapEngine:
    return request.app.state.container.get_capability_overlap_engine()

def get_capability_stability_engine(request: Request) -> CapabilityStabilityEngine:
    return request.app.state.container.get_capability_stability_engine()

def get_capability_ownership_engine(request: Request) -> CapabilityOwnershipEngine:
    return request.app.state.container.get_capability_ownership_engine()

def get_capability_drift_engine(request: Request) -> CapabilityDriftEngine:
    return request.app.state.container.get_capability_drift_engine()

def get_capability_risk_engine(request: Request) -> CapabilityRiskEngine:
    return request.app.state.container.get_capability_risk_engine()

def get_capability_placement_engine(request: Request) -> CapabilityPlacementEngine:
    return request.app.state.container.get_capability_placement_engine()

def get_capability_governance_engine(request: Request) -> CapabilityGovernanceEngine:
    return request.app.state.container.get_capability_governance_engine()

def get_capability_evolution_engine(request: Request) -> CapabilityEvolutionEngine:
    return request.app.state.container.get_capability_evolution_engine()

def get_capability_dependency_graph(request: Request) -> CapabilityDependencyGraph:
    return request.app.state.container.get_capability_dependency_graph()

def get_capability_health_engine(request: Request) -> CapabilityHealthEngine:
    return request.app.state.container.get_capability_health_engine()

def get_blast_radius_engine(request: Request) -> BlastRadiusEngine:
    return request.app.state.container.get_blast_radius_engine()

def get_capability_query_engine(request: Request) -> CapabilityQueryEngine:
    return request.app.state.container.get_capability_query_engine()

def get_capability_summary(request: Request) -> CapabilitySummary:
    return request.app.state.container.get_capability_summary()

def get_capability_boundary_engine(request: Request) -> CapabilityBoundaryEngine:
    return request.app.state.container.get_capability_boundary_engine()

def get_capability_cohesion_engine(request: Request) -> CapabilityCohesionEngine:
    return request.app.state.container.get_capability_cohesion_engine()

def get_capability_coupling_engine(request: Request) -> CapabilityCouplingEngine:
    return request.app.state.container.get_capability_coupling_engine()

def get_taxonomy_learning_engine(request: Request) -> TaxonomyLearningEngine:
    return request.app.state.container.get_taxonomy_learning_engine()

def get_capability_embedding(request: Request) -> CapabilityEmbedding:
    return request.app.state.container.get_capability_embedding()


# Phase 7A Reasoning Intelligence Layer
from src.application.reasoning.reasoning_query_engine import ReasoningQueryEngine
from src.application.reasoning.reasoning_cache import ReasoningCache
from src.application.reasoning.reasoning_strategy_registry import ReasoningStrategyRegistry


def get_reasoning_query_engine(request: Request) -> ReasoningQueryEngine:
    return request.app.state.container.get_reasoning_query_engine()


def get_reasoning_cache(request: Request) -> ReasoningCache:
    return request.app.state.container.get_reasoning_cache()


def get_reasoning_strategy_registry(request: Request) -> ReasoningStrategyRegistry:
    return request.app.state.container.get_reasoning_strategy_registry()

# Phase 7B Architecture Intelligence Layer
from src.application.architecture.architecture_cache import ArchitectureCache
from src.application.architecture.architecture_projection_engine import ArchitectureProjectionEngine
from src.application.architecture.fitness_function_engine import FitnessFunctionEngine
from src.application.architecture.bounded_context_engine import BoundedContextEngine
from src.application.architecture.architecture_pattern_registry import ArchitecturePatternRegistry
from src.application.architecture.architecture_reasoning_engine import ArchitectureReasoningEngine
from src.application.architecture.invariant_reasoning_engine import InvariantReasoningEngine
from src.application.architecture.architecture_similarity_engine import ArchitectureSimilarityEngine
from src.application.architecture.architecture_benchmark_engine import ArchitectureBenchmarkEngine
from src.application.architecture.drift_reasoning_engine import DriftReasoningEngine
from src.application.architecture.architecture_timeline_engine import ArchitectureTimelineEngine
from src.application.architecture.ownership_reasoning_engine import OwnershipReasoningEngine
from src.application.architecture.refactoring_reasoning_engine import RefactoringReasoningEngine
from src.application.architecture.architecture_recommendation_engine import ArchitectureRecommendationEngine
from src.application.architecture.architecture_artifact_service import ArchitectureArtifactService

def get_architecture_cache(request: Request) -> ArchitectureCache:
    return request.app.state.container.get_architecture_cache()

def get_architecture_projection_engine(request: Request) -> ArchitectureProjectionEngine:
    return request.app.state.container.get_architecture_projection_engine()

def get_fitness_function_engine(request: Request) -> FitnessFunctionEngine:
    return request.app.state.container.get_fitness_function_engine()

def get_bounded_context_engine(request: Request) -> BoundedContextEngine:
    return request.app.state.container.get_bounded_context_engine()

def get_architecture_pattern_registry(request: Request) -> ArchitecturePatternRegistry:
    return request.app.state.container.get_architecture_pattern_registry()

def get_architecture_reasoning_engine(request: Request) -> ArchitectureReasoningEngine:
    return request.app.state.container.get_architecture_reasoning_engine()

def get_invariant_reasoning_engine(request: Request) -> InvariantReasoningEngine:
    return request.app.state.container.get_invariant_reasoning_engine()

def get_architecture_similarity_engine(request: Request) -> ArchitectureSimilarityEngine:
    return request.app.state.container.get_architecture_similarity_engine()

def get_architecture_benchmark_engine(request: Request) -> ArchitectureBenchmarkEngine:
    return request.app.state.container.get_architecture_benchmark_engine()

def get_drift_reasoning_engine(request: Request) -> DriftReasoningEngine:
    return request.app.state.container.get_drift_reasoning_engine()

def get_architecture_timeline_engine(request: Request) -> ArchitectureTimelineEngine:
    return request.app.state.container.get_architecture_timeline_engine()

def get_ownership_reasoning_engine(request: Request) -> OwnershipReasoningEngine:
    return request.app.state.container.get_ownership_reasoning_engine()

def get_refactoring_reasoning_engine(request: Request) -> RefactoringReasoningEngine:
    return request.app.state.container.get_refactoring_reasoning_engine()

def get_architecture_recommendation_engine(request: Request) -> ArchitectureRecommendationEngine:
    return request.app.state.container.get_architecture_recommendation_engine()

def get_architecture_artifact_service(request: Request) -> ArchitectureArtifactService:
    return request.app.state.container.get_architecture_artifact_service()
