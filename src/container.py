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

from src.application.services.ontology_registry import OntologyRegistryService
from src.application.services.logic_extraction_orchestrator import LogicExtractionOrchestrator
from src.application.services.logic_evolution_service import LogicEvolutionService


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
            logic_orchestrator=self.logic_extraction_orchestrator
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

