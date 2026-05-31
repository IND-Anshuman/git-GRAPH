from typing import Callable, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import Settings
from src.application.use_cases.ingest_repository import IngestRepositoryUseCase
from src.application.use_cases.get_repository import GetRepositoryUseCase
from src.application.use_cases.query_entities import QueryEntitiesUseCase
from src.application.use_cases.query_relationships import QueryRelationshipsUseCase

from src.infrastructure.git.gitpython_adapter import GitPythonAdapter
from src.infrastructure.parsing.parser_service import TreeSitterParserService
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.scanning.file_scanner import FileSystemScanner
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.infrastructure.extraction.entity_extractor import EntityExtractorService
from src.infrastructure.extraction.relationship_extractor import RelationshipExtractorService
from src.domain.services.identity_service import EntityIdentityService

class Container:
    def __init__(self, config: Settings):
        self.config = config
        
        # Setup Database Engine
        db_url = config.database_url.replace("+asyncpg", "")  # Convert to sync driver for standard UoW
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

    def get_uow_factory(self) -> Callable:
        return lambda: SqlAlchemyUnitOfWork(self.session_factory)

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
