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

class Container:
    def __init__(self, config: Settings):
        self.config = config
        
        # Setup Database Engine
        db_url = config.database_url.replace("+asyncpg", "")  # Convert to sync driver for standard UoW
        # Avoid async pg driver prefix if present
        # In SQLite or Postgres, create engine:
        if db_url.startswith("sqlite"):
            from sqlalchemy.pool import StaticPool
            self.engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
        else:
            self.engine = create_engine(db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        
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


    def get_uow_factory(self) -> Callable:
        # Resolve class using lambda and create database connection wrapper
        # To avoid class instantiation, we use self.engine wrapper or pass self directly.
        # But SqlAlchemyUnitOfWork was the typo, we use SQLAlchemyUnitOfWork.
        # However, unit_of_work expects a DatabaseEngine instance, not sessionmaker!
        # Let's check how the DatabaseEngine is structured. Let's look at database.py or unit_of_work.__init__
        # In unit_of_work.py:
        #   def __init__(self, db_engine: DatabaseEngine) -> None:
        # Wait! DatabaseEngine is imported from: src.infrastructure.persistence.database
        # Let's instantiate DatabaseEngine or just pass an object that matches it.
        # In unit_of_work.py line 27:
        #   self._session = self._db_engine.session_factory()
        # So db_engine must have a session_factory property!
        # Let's see what is inside src/infrastructure/persistence/database.py. Let's pass a mock DatabaseEngine.
        # Let's inspect database.py first.
        class DatabaseEngineMock:
            def __init__(self, session_factory):
                self.session_factory = session_factory
        return lambda: SQLAlchemyUnitOfWork(DatabaseEngineMock(self.session_factory))

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
            detect_concepts_use_case=self.detect_concepts_use_case
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


