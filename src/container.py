from typing import Callable, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import Settings
from src.application.use_cases.ingest_repository import IngestRepositoryUseCase
from src.application.use_cases.get_repository import GetRepositoryUseCase
from src.application.use_cases.query_entities import QueryEntitiesUseCase
from src.application.use_cases.query_relationships import QueryRelationshipsUseCase
from src.application.use_cases.scan_repository_history import ScanRepositoryHistoryUseCase
from src.application.use_cases.get_commits import GetCommitsUseCase
from src.application.use_cases.get_entity_history import GetEntityHistoryUseCase
from src.application.use_cases.get_commit_changes import GetCommitChangesUseCase
from src.application.use_cases.get_repository_timeline import GetRepositoryTimelineUseCase
from src.application.use_cases.reconstruct_graph import ReconstructGraphUseCase

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
            identity_service=self.identity_service
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
            identity_service=self.identity_service
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
