"""Use case for ingesting a repository into the knowledge graph."""

import time
import uuid
import logging
import threading
from typing import Callable, Any
from datetime import datetime, timezone

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
from src.application.jobs.ingestion_job import IngestionJob

logger = logging.getLogger(__name__)

def trigger_background_jobs(repository_id: uuid.UUID, uow_factory: Callable[[], IUnitOfWork], calibration_engine: Any, concept_discovery_engine: Any, storage_root: str):
    """Triggers the post-ingestion job sequence (Enrichment -> Concept -> Capability -> Reasoning -> Pruning) in a background thread."""
    def run_jobs():
        try:
            logger.info(f"Starting background post-ingestion jobs for repository: {repository_id}")
            
            # 1. Graph Enrichment Job
            from src.application.jobs.graph_enrichment_job import GraphEnrichmentJob
            enrich_job = GraphEnrichmentJob(uow_factory, calibration_engine)
            enrich_res = enrich_job.run(repository_id)
            logger.info(f"Graph Enrichment Job completed: {enrich_res}")
            
            # 2. Concept Job
            from src.application.jobs.concept_job import ConceptJob
            concept_job = ConceptJob(concept_discovery_engine, uow_factory)
            concept_res = concept_job.run(repository_id)
            logger.info(f"Concept Job completed: {concept_res}")
            
            # 3. Capability Job
            from src.application.jobs.capability_job import CapabilityJob
            cap_job = CapabilityJob(uow_factory)
            cap_res = cap_job.run(repository_id)
            logger.info(f"Capability Job completed: {cap_res}")
            
            # 4. Reasoning Job
            from src.application.jobs.reasoning_job import ReasoningJob
            reasoning_job = ReasoningJob(uow_factory)
            reason_res = reasoning_job.run(repository_id)
            logger.info(f"Reasoning Job completed: {reason_res}")
            
            # 5. Evidence Storage Pruning Service (HOT/WARM/COLD)
            from src.application.services.evidence_storage_policy import EvidenceStoragePruningService
            archive_dir = os.path.join(storage_root, "archives") if "os" in globals() else f"{storage_root}/archives"
            import os
            archive_dir = os.path.join(storage_root, "archives")
            pruning_service = EvidenceStoragePruningService(uow_factory, archive_dir)
            pruning_service.prune_repository_evidence(repository_id)
            logger.info(f"Evidence Storage Pruning completed for repository: {repository_id}")
            
        except Exception as ex:
            logger.error(f"Error in background post-ingestion jobs: {ex}", exc_info=True)
            
    thread = threading.Thread(target=run_jobs, daemon=True)
    thread.start()

class IngestRepositoryUseCase:
    """Handles the synchronous ingestion phase and triggers asynchronous enrichment and reasoning."""
    
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
        calibration_engine: Any = None,
        concept_discovery_engine: Any = None,
        reconstruction_service: Any = None
    ):
        self.git_adapter = git_adapter
        self.uow_factory = uow_factory
        self.storage_root = storage_root
        self.reconstruction_service = reconstruction_service
        self.calibration_engine = calibration_engine
        self.concept_discovery_engine = concept_discovery_engine
        
        self.pipeline = IngestionPipeline(
            git_adapter=git_adapter,
            file_scanner=file_scanner,
            parser=parser,
            entity_extractor=entity_extractor,
            relationship_extractor=relationship_extractor,
            identity_service=identity_service
        )
        self.ingestion_job = IngestionJob(self.pipeline, uow_factory)

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
            
            # Execute core IngestionJob synchronously
            job_result = self.ingestion_job.run(repository, self.storage_root)
            
            with self.uow_factory() as uow:
                repo_in_db = uow.repositories.get_by_id(repository_id)
                if repo_in_db:
                    repo_in_db.status = AnalysisStatus.COMPLETED
                    repo_in_db.updated_at = datetime.now(timezone.utc)
                    repo_in_db.metadata["files_count"] = job_result["files_scanned"]
                    repo_in_db.metadata["entities_count"] = job_result["entities_extracted"]
                    repo_in_db.metadata["relationships_count"] = job_result["relationships_extracted"]
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
                        commit_exists = uow_recon.commits.get_by_hash(commit_hash) is not None
                        if commit_exists:
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
                    diff_throughput_nodes_sec=0.0,
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

            # Trigger asynchronous post-ingestion job sequence
            if self.calibration_engine and self.concept_discovery_engine:
                trigger_background_jobs(
                    repository_id=repository_id.value,
                    uow_factory=self.uow_factory,
                    calibration_engine=self.calibration_engine,
                    concept_discovery_engine=self.concept_discovery_engine,
                    storage_root=self.storage_root
                )

            return IngestionResultResponse(
                repository_id=str(repository_id),
                status=AnalysisStatus.COMPLETED.name,
                files_scanned=job_result["files_scanned"],
                entities_extracted=job_result["entities_extracted"],
                relationships_extracted=job_result["relationships_extracted"],
                errors=job_result["errors"]
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
