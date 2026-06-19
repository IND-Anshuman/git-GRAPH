from typing import Callable, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import Settings
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

# Phase 4 Use Cases
from src.application.use_cases.detect_concepts import DetectConceptsUseCase
from src.application.use_cases.get_concepts import GetConceptsUseCase
from src.application.use_cases.get_concept_evolution import GetConceptEvolutionUseCase
from src.application.use_cases.get_concept_relationships import GetConceptRelationshipsUseCase
from src.application.use_cases.get_concept_drift import GetConceptDriftUseCase
from src.application.use_cases.get_concept_explanation import GetConceptExplanationUseCase

# Phase 3 Use Cases
from src.application.use_cases.extract_logic_use_case import ExtractLogicUseCase
from src.application.use_cases.get_entity_logic_use_case import GetEntityLogicUseCase
from src.application.use_cases.get_entity_logic_history_use_case import GetEntityLogicHistoryUseCase
from src.application.use_cases.get_behavior_evolution_use_case import GetBehaviorEvolutionUseCase
from src.application.use_cases.get_logic_evidence_use_case import GetLogicEvidenceUseCase
from src.application.use_cases.get_behavior_explanation_use_case import GetBehaviorExplanationUseCase
from src.application.use_cases.get_behavior_drift_use_case import GetBehaviorDriftUseCase
from src.application.use_cases.validate_logic_use_case import ValidateLogicUseCase

# Phase 3 Services & Engines
from src.infrastructure.logic.ast_feature_extractor import TreeSitterASTFeatureExtractor
from src.infrastructure.logic.logic_fingerprint_engine import LogicFingerprintEngine
from src.infrastructure.logic.ontology_loader import OntologyLoader
from src.infrastructure.logic.pattern_registry import PatternRegistry
from src.infrastructure.logic.logic_extraction_engine import LogicExtractionEngine
from src.infrastructure.logic.logic_similarity_engine import LogicSimilarityEngine
from src.infrastructure.logic.logic_diff_engine import LogicDiffEngine
from src.infrastructure.logic.behavior_drift_engine import BehaviorDriftEngine

from src.application.services.ontology_registry import OntologyRegistryService, ConceptOntologyRegistry
from src.application.services.logic_extraction_orchestrator import LogicExtractionOrchestrator
from src.application.services.logic_evolution_service import LogicEvolutionService

# Phase 4 Services & Engines
from src.application.services.concept_detection_engine import ConceptDetectionEngine
from src.application.services.concept_relationship_engine import ConceptRelationshipEngine
from src.application.services.concept_cluster_engine import ConceptClusterEngine
from src.application.services.concept_metrics_engine import ConceptMetricsEngine
from src.application.services.concept_drift_engine import ConceptDriftEngine
from src.application.services.concept_evolution_engine import ConceptEvolutionEngine
from src.application.services.concept_explanation_engine import ConceptExplanationEngine
from src.application.services.concept_backfill_service import ConceptBackfillService

# Phase 4.5 Semantic Expansion Bounded Context
from src.application.semantic.behavior_registry.canonical_registry import CanonicalRegistry
from src.application.semantic.type_resolution.type_resolution_engine import TypeResolutionEngine
from src.application.semantic.normalization.semantic_normalizer import SemanticNormalizer

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

from src.infrastructure.git.gitpython_adapter import GitPythonAdapter
from src.infrastructure.git.rename_detection import RenameDetector
from src.infrastructure.git.move_detection import MoveDetector
from src.infrastructure.git.temporal_diff_engine import TemporalDiffEngine
from src.infrastructure.parsing.parser_service import TreeSitterParserService
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.scanning.file_scanner import FileSystemScanner
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.infrastructure.extraction.entity_extractor import EntityExtractorService
from src.infrastructure.extraction.relationship_extractor import RelationshipExtractorService
from src.application.services.historical_reconstruction import HistoricalReconstructionService
from src.application.services.temporal_integrity_service import TemporalIntegrityService
from src.application.services.reconstruction_validation_engine import ReconstructionValidationEngine
from src.application.services.accuracy_engine import AccuracyEngine
from src.application.services.seid_validation_engine import SEIDValidationEngine
from src.application.services.health_score_engine import HealthScoreEngine
from src.application.services.temporal_explorer import TemporalExplorer
from src.application.services.temporal_replay_service import TemporalReplayService
from src.domain.services.identity_service import EntityIdentityService

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

# Phase 7A Reasoning Intelligence Layer
from src.application.reasoning.reasoning_strategy_registry import ReasoningStrategyRegistry
from src.application.reasoning.reasoning_cache import ReasoningCache
from src.application.reasoning.reasoning_artifact_service import ReasoningArtifactService
from src.application.reasoning.reasoning_query_engine import ReasoningQueryEngine
from src.application.architecture.architecture_strategies import (
    ArchitectureStyleStrategy,
    FitnessStrategy,
    InvariantStrategy,
    DriftArchStrategy,
    OwnershipArchStrategy,
    RefactoringStrategy,
    RecommendationStrategy,
    SimilarityStrategy,
    BenchmarkStrategy,
    TimelineStrategy,
)


class Container:
    def __init__(self, config: Settings):
        self.config = config
        
        # Setup Database Engine
        from src.infrastructure.persistence.database import DatabaseEngine
        db_url = config.database_url.replace("+asyncpg", "")  # Convert to sync driver for standard UoW
        self.db_engine = DatabaseEngine(db_url)
        # For SQLite in testing, we configure check_same_thread=False
        if db_url.startswith("sqlite"):
            from sqlalchemy.pool import StaticPool
            self.db_engine.engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
            self.db_engine.session_factory = sessionmaker(
                bind=self.db_engine.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
        
        # Setup Infrastructure
        self.git_adapter = GitPythonAdapter()
        
        # Parser setup requires LanguageRegistry
        self.language_registry = LanguageRegistry()
        self.parser = TreeSitterParserService(self.language_registry)
        
        self.file_scanner = FileSystemScanner()
        
        self.identity_service = EntityIdentityService()
        self.entity_extractor = EntityExtractorService(self.language_registry, self.identity_service)
        self.relationship_extractor = RelationshipExtractorService(self.language_registry)
        
        # Temporal engine services
        self.rename_detector = RenameDetector()
        self.move_detector = MoveDetector()
        self.diff_engine = TemporalDiffEngine(self.rename_detector, self.move_detector)
        self.reconstruction_service = HistoricalReconstructionService()
        self.temporal_integrity_service = TemporalIntegrityService()
        self.reconstruction_validation_engine = ReconstructionValidationEngine(
            reconstruction_service=self.reconstruction_service,
            git_adapter=self.git_adapter,
            file_scanner=self.file_scanner,
            parser=self.parser,
            entity_extractor=self.entity_extractor,
            relationship_extractor=self.relationship_extractor,
            identity_service=self.identity_service
        )
        self.accuracy_engine = AccuracyEngine(self.reconstruction_validation_engine)
        self.seid_validation_engine = SEIDValidationEngine()
        self.health_score_engine = HealthScoreEngine(self.seid_validation_engine)
        self.temporal_explorer = TemporalExplorer()
        self.temporal_replay_service = TemporalReplayService(self.reconstruction_service)

        # Phase 3 Behavioral Intelligence setup
        self.in_memory_pattern_registry = PatternRegistry()
        self.ontology_loader = OntologyLoader()
        self.ast_feature_extractor = TreeSitterASTFeatureExtractor()
        self.logic_fingerprint_engine = LogicFingerprintEngine()
        self.logic_similarity_engine = LogicSimilarityEngine()
        self.logic_diff_engine = LogicDiffEngine()
        self.behavior_drift_engine = BehaviorDriftEngine()

        self.logic_extraction_engine = LogicExtractionEngine(
            extractor=self.ast_feature_extractor,
            fingerprinter=self.logic_fingerprint_engine,
            registry=self.in_memory_pattern_registry
        )

        self.ontology_registry_service = OntologyRegistryService(
            uow_factory=self.get_uow_factory(),
            loader=self.ontology_loader,
            in_memory_patterns=self.in_memory_pattern_registry
        )
        self.logic_evolution_service = LogicEvolutionService(
            uow_factory=self.get_uow_factory()
        )
        self.logic_extraction_orchestrator = LogicExtractionOrchestrator(
            uow_factory=self.get_uow_factory(),
            git_adapter=self.git_adapter,
            parser=self.parser,
            extraction_engine=self.logic_extraction_engine,
            similarity_engine=self.logic_similarity_engine,
            diff_engine=self.logic_diff_engine,
            drift_engine=self.behavior_drift_engine
        )

        # Phase 4 Concept Intelligence setup
        self.concept_ontology_registry = ConceptOntologyRegistry()
        self.concept_detection_engine = ConceptDetectionEngine(
            ontology_registry=self.concept_ontology_registry
        )
        self.concept_relationship_engine = ConceptRelationshipEngine(
            reconstruction_service=self.reconstruction_service
        )
        self.concept_cluster_engine = ConceptClusterEngine()
        self.concept_metrics_engine = ConceptMetricsEngine()
        self.concept_drift_engine = ConceptDriftEngine()
        self.concept_evolution_engine = ConceptEvolutionEngine()
        self.concept_explanation_engine = ConceptExplanationEngine()

        # Phase 4.5 Semantic Expansion setup
        self.canonical_registry = CanonicalRegistry()
        self.type_resolution_engine = TypeResolutionEngine()
        self.semantic_normalizer = SemanticNormalizer(
            registry=self.canonical_registry,
            type_engine=self.type_resolution_engine
        )

        self.detect_concepts_use_case = DetectConceptsUseCase(
            uow_factory=self.get_uow_factory(),
            detection_engine=self.concept_detection_engine,
            relationship_engine=self.concept_relationship_engine,
            metrics_engine=self.concept_metrics_engine,
            evolution_engine=self.concept_evolution_engine,
            drift_engine=self.concept_drift_engine,
            explanation_engine=self.concept_explanation_engine,
            cluster_engine=self.concept_cluster_engine
        )

        self.concept_backfill_service = ConceptBackfillService(
            uow_factory=self.get_uow_factory(),
            detect_concepts_use_case=self.detect_concepts_use_case
        )

        # Phase 5A Discovery / Meta-Ontology Bounded Context
        self.embedding_registry = EmbeddingRegistry(uow=self.get_uow_factory()())
        self.calibration_engine = ConfidenceCalibrationEngine()
        self.schema_registry = SchemaRegistry(uow=self.get_uow_factory()())
        self.governance_manager = GovernanceManager(uow=self.get_uow_factory()())
        self.entity_discovery_engine = EntityDiscoveryEngine(
            uow=self.get_uow_factory()(),
            embedding_registry=self.embedding_registry,
            schema_registry=self.schema_registry,
            calibration_engine=self.calibration_engine,
        )
        self.relationship_discovery_engine = RelationshipDiscoveryEngine(
            uow=self.get_uow_factory()(),
            calibration_engine=self.calibration_engine,
        )
        self.behavior_discovery_engine = BehaviorDiscoveryEngine(
            uow=self.get_uow_factory()(),
            schema_registry=self.schema_registry,
            calibration_engine=self.calibration_engine,
        )
        self.concept_discovery_engine = ConceptDiscoveryEngine(
            uow=self.get_uow_factory()(),
            schema_registry=self.schema_registry,
            embedding_registry=self.embedding_registry,
            calibration_engine=self.calibration_engine,
        )
        self.flow_discovery_engine = FlowDiscoveryEngine(
            uow=self.get_uow_factory()(),
        )
        self.semantic_evolution_engine = SemanticEvolutionEngine(
            uow=self.get_uow_factory()(),
            reconstructor=self.reconstruction_service,
        )

        # Phase 6 Capability Intelligence Layer
        self.capability_discovery_engine = CapabilityDiscoveryEngine()
        self.capability_confidence_engine = CapabilityConfidenceEngine()
        self.capability_overlap_engine = CapabilityOverlapEngine()
        self.capability_stability_engine = CapabilityStabilityEngine()
        self.capability_ownership_engine = CapabilityOwnershipEngine()
        self.capability_drift_engine = CapabilityDriftEngine()
        self.capability_risk_engine = CapabilityRiskEngine()
        self.capability_placement_engine = CapabilityPlacementEngine()
        self.capability_governance_engine = CapabilityGovernanceEngine()
        self.capability_evolution_engine = CapabilityEvolutionEngine()
        self.capability_dependency_graph = CapabilityDependencyGraph()
        self.capability_health_engine = CapabilityHealthEngine()
        self.blast_radius_engine = BlastRadiusEngine()
        self.capability_query_engine = CapabilityQueryEngine()
        self.capability_summary = CapabilitySummary()
        self.capability_boundary_engine = CapabilityBoundaryEngine()
        self.capability_cohesion_engine = CapabilityCohesionEngine()
        self.capability_coupling_engine = CapabilityCouplingEngine()
        self.taxonomy_learning_engine = TaxonomyLearningEngine()
        self.capability_embedding = CapabilityEmbedding()

        # Phase 7A Reasoning Intelligence Layer
        self.reasoning_strategy_registry = ReasoningStrategyRegistry.default()
        
        # Register Phase 7B Architecture Strategies
        self.reasoning_strategy_registry.register(ArchitectureStyleStrategy())
        self.reasoning_strategy_registry.register(FitnessStrategy())
        self.reasoning_strategy_registry.register(InvariantStrategy())
        self.reasoning_strategy_registry.register(DriftArchStrategy())
        self.reasoning_strategy_registry.register(OwnershipArchStrategy())
        self.reasoning_strategy_registry.register(RefactoringStrategy())
        self.reasoning_strategy_registry.register(RecommendationStrategy())
        self.reasoning_strategy_registry.register(SimilarityStrategy())
        self.reasoning_strategy_registry.register(BenchmarkStrategy())
        self.reasoning_strategy_registry.register(TimelineStrategy())

        self.reasoning_cache = ReasoningCache(max_size=512)
        self.reasoning_artifact_service = ReasoningArtifactService()
        self.reasoning_query_engine = ReasoningQueryEngine(
            strategy_registry=self.reasoning_strategy_registry,
            cache=self.reasoning_cache,
            uow_factory=self.get_uow_factory(),
            artifact_service=self.reasoning_artifact_service,
            persist_artifacts=True,
        )

        # Phase 7B Architecture Intelligence Layer
        self.architecture_cache = ArchitectureCache()
        self.architecture_projection_engine = ArchitectureProjectionEngine()
        self.fitness_function_engine = FitnessFunctionEngine()
        self.bounded_context_engine = BoundedContextEngine()
        self.architecture_pattern_registry = ArchitecturePatternRegistry()
        self.architecture_reasoning_engine = ArchitectureReasoningEngine()
        self.invariant_reasoning_engine = InvariantReasoningEngine()
        self.architecture_similarity_engine = ArchitectureSimilarityEngine()
        self.architecture_benchmark_engine = ArchitectureBenchmarkEngine()
        self.drift_reasoning_engine = DriftReasoningEngine()
        self.architecture_timeline_engine = ArchitectureTimelineEngine()
        self.ownership_reasoning_engine = OwnershipReasoningEngine()
        self.refactoring_reasoning_engine = RefactoringReasoningEngine()
        self.architecture_recommendation_engine = ArchitectureRecommendationEngine()
        self.architecture_artifact_service = ArchitectureArtifactService(self.get_uow_factory()())

    def get_uow_factory(self) -> Callable:
        return lambda: SQLAlchemyUnitOfWork(self.db_engine)

    def get_ingest_repository_use_case(self) -> IngestRepositoryUseCase:
        return IngestRepositoryUseCase(
            git_adapter=self.git_adapter,
            file_scanner=self.file_scanner,
            parser=self.parser,
            entity_extractor=self.entity_extractor,
            relationship_extractor=self.relationship_extractor,
            uow_factory=self.get_uow_factory(),
            storage_root=self.config.storage_root,
            identity_service=self.identity_service,
            calibration_engine=self.calibration_engine,
            concept_discovery_engine=self.concept_discovery_engine,
            reconstruction_service=self.reconstruction_service
        )

    def get_get_repository_use_case(self) -> GetRepositoryUseCase:
        return GetRepositoryUseCase(uow_factory=self.get_uow_factory())

    def get_query_entities_use_case(self) -> QueryEntitiesUseCase:
        return QueryEntitiesUseCase(uow_factory=self.get_uow_factory())

    def get_query_relationships_use_case(self) -> QueryRelationshipsUseCase:
        return QueryRelationshipsUseCase(uow_factory=self.get_uow_factory())

    def get_scan_repository_history_use_case(self) -> ScanRepositoryHistoryUseCase:
        return ScanRepositoryHistoryUseCase(
            git_adapter=self.git_adapter,
            file_scanner=self.file_scanner,
            parser=self.parser,
            entity_extractor=self.entity_extractor,
            relationship_extractor=self.relationship_extractor,
            diff_engine=self.diff_engine,
            uow_factory=self.get_uow_factory(),
            identity_service=self.identity_service,
            reconstruction_service=self.reconstruction_service,
            logic_orchestrator=self.logic_extraction_orchestrator,
            detect_concepts_use_case=self.detect_concepts_use_case,
            calibration_engine=self.calibration_engine,
            concept_discovery_engine=self.concept_discovery_engine
        )

    def get_get_commits_use_case(self) -> GetCommitsUseCase:
        return GetCommitsUseCase(uow_factory=self.get_uow_factory())

    def get_entity_history_use_case(self) -> GetEntityHistoryUseCase:
        return GetEntityHistoryUseCase(uow_factory=self.get_uow_factory())

    def get_commit_changes_use_case(self) -> GetCommitChangesUseCase:
        return GetCommitChangesUseCase(uow_factory=self.get_uow_factory())

    def get_repository_timeline_use_case(self) -> GetRepositoryTimelineUseCase:
        return GetRepositoryTimelineUseCase(uow_factory=self.get_uow_factory())

    def get_reconstruct_graph_use_case(self) -> ReconstructGraphUseCase:
        return ReconstructGraphUseCase(
            reconstruction_service=self.reconstruction_service,
            uow_factory=self.get_uow_factory()
        )

    def get_extract_logic_use_case(self) -> ExtractLogicUseCase:
        return ExtractLogicUseCase(
            uow_factory=self.get_uow_factory(),
            orchestrator=self.logic_extraction_orchestrator
        )

    def get_get_entity_logic_use_case(self) -> GetEntityLogicUseCase:
        return GetEntityLogicUseCase(uow_factory=self.get_uow_factory())

    def get_get_entity_logic_history_use_case(self) -> GetEntityLogicHistoryUseCase:
        return GetEntityLogicHistoryUseCase(uow_factory=self.get_uow_factory())

    def get_get_behavior_evolution_use_case(self) -> GetBehaviorEvolutionUseCase:
        return GetBehaviorEvolutionUseCase(
            uow_factory=self.get_uow_factory(),
            evolution_service=self.logic_evolution_service
        )

    def get_get_logic_evidence_use_case(self) -> GetLogicEvidenceUseCase:
        return GetLogicEvidenceUseCase(uow_factory=self.get_uow_factory())

    def get_get_behavior_explanation_use_case(self) -> GetBehaviorExplanationUseCase:
        return GetBehaviorExplanationUseCase(uow_factory=self.get_uow_factory())

    def get_get_behavior_drift_use_case(self) -> GetBehaviorDriftUseCase:
        return GetBehaviorDriftUseCase(uow_factory=self.get_uow_factory())

    def get_validate_logic_use_case(self) -> ValidateLogicUseCase:
        return ValidateLogicUseCase(uow_factory=self.get_uow_factory())

    def get_delete_repository_use_case(self) -> DeleteRepositoryUseCase:
        return DeleteRepositoryUseCase(uow_factory=self.get_uow_factory())

    def get_detect_concepts_use_case(self) -> DetectConceptsUseCase:
        return self.detect_concepts_use_case

    def get_get_concepts_use_case(self) -> GetConceptsUseCase:
        return GetConceptsUseCase(uow_factory=self.get_uow_factory())

    def get_get_concept_evolution_use_case(self) -> GetConceptEvolutionUseCase:
        return GetConceptEvolutionUseCase(uow_factory=self.get_uow_factory())

    def get_get_concept_relationships_use_case(self) -> GetConceptRelationshipsUseCase:
        return GetConceptRelationshipsUseCase(uow_factory=self.get_uow_factory())

    def get_get_concept_drift_use_case(self) -> GetConceptDriftUseCase:
        return GetConceptDriftUseCase(
            uow_factory=self.get_uow_factory(),
            drift_engine=self.concept_drift_engine
        )

    def get_get_concept_explanation_use_case(self) -> GetConceptExplanationUseCase:
        return GetConceptExplanationUseCase(uow_factory=self.get_uow_factory())

    def get_concept_backfill_service(self) -> ConceptBackfillService:
        return self.concept_backfill_service

    def get_canonical_registry(self) -> CanonicalRegistry:
        return self.canonical_registry

    def get_type_resolution_engine(self) -> TypeResolutionEngine:
        return self.type_resolution_engine

    def get_semantic_normalizer(self) -> SemanticNormalizer:
        return self.semantic_normalizer

    def get_embedding_registry(self) -> EmbeddingRegistry:
        return self.embedding_registry

    def get_calibration_engine(self) -> ConfidenceCalibrationEngine:
        return self.calibration_engine

    def get_schema_registry(self) -> SchemaRegistry:
        return self.schema_registry

    def get_governance_manager(self) -> GovernanceManager:
        return self.governance_manager

    def get_entity_discovery_engine(self) -> EntityDiscoveryEngine:
        return self.entity_discovery_engine

    def get_relationship_discovery_engine(self) -> RelationshipDiscoveryEngine:
        return self.relationship_discovery_engine

    def get_behavior_discovery_engine(self) -> BehaviorDiscoveryEngine:
        return self.behavior_discovery_engine

    def get_concept_discovery_engine(self) -> ConceptDiscoveryEngine:
        return self.concept_discovery_engine

    def get_flow_discovery_engine(self) -> FlowDiscoveryEngine:
        return self.flow_discovery_engine

    def get_semantic_evolution_engine(self) -> SemanticEvolutionEngine:
        return self.semantic_evolution_engine

    def get_capability_discovery_engine(self) -> CapabilityDiscoveryEngine:
        return self.capability_discovery_engine

    def get_capability_confidence_engine(self) -> CapabilityConfidenceEngine:
        return self.capability_confidence_engine

    def get_capability_overlap_engine(self) -> CapabilityOverlapEngine:
        return self.capability_overlap_engine

    def get_capability_stability_engine(self) -> CapabilityStabilityEngine:
        return self.capability_stability_engine

    def get_capability_ownership_engine(self) -> CapabilityOwnershipEngine:
        return self.capability_ownership_engine

    def get_capability_drift_engine(self) -> CapabilityDriftEngine:
        return self.capability_drift_engine

    def get_capability_risk_engine(self) -> CapabilityRiskEngine:
        return self.capability_risk_engine

    def get_capability_placement_engine(self) -> CapabilityPlacementEngine:
        return self.capability_placement_engine

    def get_capability_governance_engine(self) -> CapabilityGovernanceEngine:
        return self.capability_governance_engine

    def get_capability_evolution_engine(self) -> CapabilityEvolutionEngine:
        return self.capability_evolution_engine

    def get_capability_dependency_graph(self) -> CapabilityDependencyGraph:
        return self.capability_dependency_graph

    def get_capability_health_engine(self) -> CapabilityHealthEngine:
        return self.capability_health_engine

    def get_blast_radius_engine(self) -> BlastRadiusEngine:
        return self.blast_radius_engine

    def get_capability_query_engine(self) -> CapabilityQueryEngine:
        return self.capability_query_engine

    def get_capability_summary(self) -> CapabilitySummary:
        return self.capability_summary

    def get_capability_boundary_engine(self) -> CapabilityBoundaryEngine:
        return self.capability_boundary_engine

    def get_capability_cohesion_engine(self) -> CapabilityCohesionEngine:
        return self.capability_cohesion_engine

    def get_capability_coupling_engine(self) -> CapabilityCouplingEngine:
        return self.capability_coupling_engine

    def get_taxonomy_learning_engine(self) -> TaxonomyLearningEngine:
        return self.taxonomy_learning_engine

    def get_capability_embedding(self) -> CapabilityEmbedding:
        return self.capability_embedding

    def get_reasoning_query_engine(self) -> ReasoningQueryEngine:
        return self.reasoning_query_engine

    def get_reasoning_cache(self) -> ReasoningCache:
        return self.reasoning_cache

    def get_reasoning_strategy_registry(self) -> ReasoningStrategyRegistry:
        return self.reasoning_strategy_registry

    def get_architecture_cache(self) -> ArchitectureCache:
        return self.architecture_cache

    def get_architecture_projection_engine(self) -> ArchitectureProjectionEngine:
        return self.architecture_projection_engine

    def get_fitness_function_engine(self) -> FitnessFunctionEngine:
        return self.fitness_function_engine

    def get_bounded_context_engine(self) -> BoundedContextEngine:
        return self.bounded_context_engine

    def get_architecture_pattern_registry(self) -> ArchitecturePatternRegistry:
        return self.architecture_pattern_registry

    def get_architecture_reasoning_engine(self) -> ArchitectureReasoningEngine:
        return self.architecture_reasoning_engine

    def get_invariant_reasoning_engine(self) -> InvariantReasoningEngine:
        return self.invariant_reasoning_engine

    def get_architecture_similarity_engine(self) -> ArchitectureSimilarityEngine:
        return self.architecture_similarity_engine

    def get_architecture_benchmark_engine(self) -> ArchitectureBenchmarkEngine:
        return self.architecture_benchmark_engine

    def get_drift_reasoning_engine(self) -> DriftReasoningEngine:
        return self.drift_reasoning_engine

    def get_architecture_timeline_engine(self) -> ArchitectureTimelineEngine:
        return self.architecture_timeline_engine

    def get_ownership_reasoning_engine(self) -> OwnershipReasoningEngine:
        return self.ownership_reasoning_engine

    def get_refactoring_reasoning_engine(self) -> RefactoringReasoningEngine:
        return self.refactoring_reasoning_engine

    def get_architecture_recommendation_engine(self) -> ArchitectureRecommendationEngine:
        return self.architecture_recommendation_engine

    def get_architecture_artifact_service(self) -> ArchitectureArtifactService:
        return self.architecture_artifact_service

    @property
    def engine(self) -> Any:
        return self.db_engine.engine

    @property
    def session_factory(self) -> Any:
        return self.db_engine.session_factory
