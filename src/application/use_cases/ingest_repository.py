from typing import Callable, Any
import time
import uuid
from datetime import datetime, timezone
import logging

from src.application.ports.git_port import IGitAdapter
from src.application.ports.file_scanner_port import IFileScanner
from src.application.ports.parser_port import IParser
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.dtos.commands import IngestRepositoryCommand
from src.application.dtos.responses import IngestionResultResponse
from src.application.services.ingestion_pipeline import IngestionPipeline
from src.domain.entities import RepositoryEntity
from src.domain.entities.metrics import BenchmarkReport
from src.domain.enums import AnalysisStatus
from src.application.use_cases.scan_repository_history import get_memory_rss_bytes, get_db_size_bytes

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
        identity_service: Any,
        reconstruction_service: Any = None
    ):
        self.git_adapter = git_adapter
        self.uow_factory = uow_factory
        self.storage_root = storage_root
        self.reconstruction_service = reconstruction_service
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
            t_start = time.perf_counter()
            mem_start = get_memory_rss_bytes()
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

            # Post-ingestion benchmark telemetry collection
            try:
                commit_hash = "HEAD"
                try:
                    commit_hash = self.git_adapter.get_current_commit_hash(repository.local_path)
                except Exception as git_err:
                    logger.warning(f"Could not retrieve HEAD commit hash: {git_err}")

                recon_latency_ms = 0
                if self.reconstruction_service:
                    recon_start = time.perf_counter()
                    with self.uow_factory() as uow_recon:
                        self.reconstruction_service.reconstruct_graph_at_commit(
                            uow_recon, repository_id, commit_hash
                        )
                    recon_latency_ms = int((time.perf_counter() - recon_start) * 1000)

                db_size = 0
                with self.uow_factory() as uow_db:
                    db_size = get_db_size_bytes(uow_db._session)

                mem_end = get_memory_rss_bytes()
                max_mem_rss = max(mem_start, mem_end)

                scan_duration_ms = int((time.perf_counter() - t_start) * 1000)

                benchmark = BenchmarkReport(
                    id=uuid.uuid4(),
                    repository_id=repository_id,
                    commit_hash=commit_hash,
                    scan_duration_ms=scan_duration_ms,
                    diff_throughput_nodes_sec=0.0,  # No diff engine run during ingestion
                    reconstruction_latency_ms=recon_latency_ms,
                    db_size_bytes=db_size,
                    memory_rss_bytes=max_mem_rss,
                    measured_at=datetime.now(timezone.utc)
                )
                with self.uow_factory() as uow_bench:
                    uow_bench.metrics.save_benchmark_report(benchmark)
                    uow_bench.commit()
            except Exception as telemetry_error:
                logger.warning(f"Error collecting benchmark metrics during ingestion: {telemetry_error}", exc_info=True)

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
