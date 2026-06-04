from typing import Callable, Any
from src.application.ports.git_port import IGitAdapter
from src.application.ports.file_scanner_port import IFileScanner
from src.application.ports.parser_port import IParser
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.dtos.commands import IngestRepositoryCommand
from src.application.dtos.responses import IngestionResultResponse
from src.application.services.ingestion_pipeline import IngestionPipeline
from src.domain.entities import RepositoryEntity
from src.domain.enums import AnalysisStatus
import uuid
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class IngestRepositoryUseCase:
    def __init__(
        self,
        git_adapter: IGitAdapter,
        file_scanner: IFileScanner,
        parser: IParser,
        entity_extractor: Any,
        relationship_extractor: Any,
        uow_factory: Callable[[], IUnitOfWork],
        storage_root: str,
        identity_service: Any
    ):
        self.uow_factory = uow_factory
        self.storage_root = storage_root
        self.pipeline = IngestionPipeline(
            git_adapter=git_adapter,
            file_scanner=file_scanner,
            parser=parser,
            entity_extractor=entity_extractor,
            relationship_extractor=relationship_extractor,
            identity_service=identity_service
        )

    def execute(self, command: IngestRepositoryCommand) -> IngestionResultResponse:
        url_str = str(command.url)
        
        with self.uow_factory() as uow:
            existing = uow.repositories.get_by_url(url_str)
            if existing:
                return IngestionResultResponse(
                    repository_id=str(existing.id),
                    status=existing.status.name,
                    files_scanned=0,
                    entities_extracted=0,
                    relationships_extracted=0,
                    errors=["Repository already exists."]
                )

            from src.domain.value_objects.repository_id import RepositoryId
            repository_id = RepositoryId.generate()
            name = command.name or url_str.split("/")[-1].replace(".git", "")
            now = datetime.now(timezone.utc)
            repository = RepositoryEntity(
                id=repository_id,
                name=name,
                url=url_str,
                default_branch=command.branch,
                local_path="",
                status=AnalysisStatus.PENDING,
                created_at=now,
                updated_at=now,
                metadata={}
            )
            uow.repositories.save(repository)
            uow.commit()

        try:
            result = self.pipeline.run(repository, self.storage_root)
            
            with self.uow_factory() as uow:
                repo_in_db = uow.repositories.get_by_id(repository_id)
                if repo_in_db:
                    if result.files:
                        uow.source_files.save_batch(result.files)
                    if result.entities:
                        uow.code_entities.save_batch(result.entities)
                    if result.relationships:
                        uow.relationships.save_batch(result.relationships)
                    
                    repo_in_db.local_path = repository.local_path
                    repo_in_db.status = AnalysisStatus.COMPLETED
                    repo_in_db.updated_at = datetime.now(timezone.utc)
                    repo_in_db.metadata["files_count"] = len(result.files)
                    repo_in_db.metadata["entities_count"] = len(result.entities)
                    repo_in_db.metadata["relationships_count"] = len(result.relationships)
                    
                    uow.repositories.save(repo_in_db)
                    uow.commit()

            return IngestionResultResponse(
                repository_id=str(repository_id),
                status=AnalysisStatus.COMPLETED.name,
                files_scanned=len(result.files),
                entities_extracted=len(result.entities),
                relationships_extracted=len(result.relationships),
                errors=result.errors
            )

        except Exception as e:
            logger.error(f"Error ingesting repository {url_str}: {e}")
            with self.uow_factory() as uow:
                repo_in_db = uow.repositories.get_by_id(repository_id)
                if repo_in_db:
                    repo_in_db.status = AnalysisStatus.FAILED
                    repo_in_db.updated_at = datetime.now(timezone.utc)
                    repo_in_db.metadata["error"] = str(e)
                    uow.repositories.save(repo_in_db)
                    uow.commit()

            return IngestionResultResponse(
                repository_id=str(repository_id),
                status=AnalysisStatus.FAILED.name,
                files_scanned=0,
                entities_extracted=0,
                relationships_extracted=0,
                errors=[str(e)]
            )
