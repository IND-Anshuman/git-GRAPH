"""Use case for scanning repository Git history and populating the temporal graph."""

import datetime
import logging
import uuid
import time
import sys
from typing import Any, Callable, List
from sqlalchemy import text

from src.application.ports.git_port import IGitAdapter
from src.application.ports.file_scanner_port import IFileScanner
from src.application.ports.parser_port import IParser
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.entities.repository_snapshot import RepositorySnapshot
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.file_id import FileId
from src.domain.entities.source_file import SourceFile
from src.domain.entities.metrics import BenchmarkReport
from src.infrastructure.git.commit_walker import CommitWalker
from src.infrastructure.git.temporal_diff_engine import TemporalDiffEngine

logger = logging.getLogger(__name__)


def get_memory_rss_bytes() -> int:
    try:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes

            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            GetProcessMemoryInfo = ctypes.windll.psapi.GetProcessMemoryInfo
            GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess

            GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
            GetProcessMemoryInfo.restype = wintypes.BOOL

            process_handle = GetCurrentProcess()
            counters = PROCESS_MEMORY_COUNTERS()
            counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)

            if GetProcessMemoryInfo(process_handle, ctypes.byref(counters), counters.cb):
                return counters.WorkingSetSize
        else:
            import resource
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    except Exception:
        pass
    return 0


def get_db_size_bytes(session) -> int:
    try:
        bind_url = str(session.bind.url)
        if "postgresql" in bind_url:
            res = session.execute(text("SELECT pg_database_size(current_database())"))
            row = res.fetchone()
            if row:
                return int(row[0])
        elif "sqlite" in bind_url:
            res = session.execute(text("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()"))
            row = res.fetchone()
            if row:
                return int(row[0])
    except Exception as e:
        logger.warning(f"Could not calculate database size: {e}")
    return 0


class ScanRepositoryHistoryUseCase:
    """Orchestrates Git history walking, AST parsing per commit, and temporal diff persistence."""

    def __init__(
        self,
        git_adapter: IGitAdapter,
        file_scanner: IFileScanner,
        parser: IParser,
        entity_extractor: Any,
        relationship_extractor: Any,
        diff_engine: TemporalDiffEngine,
        uow_factory: Callable[[], IUnitOfWork],
        identity_service: Any,
        reconstruction_service: Any = None,
        logic_orchestrator: Any = None,
        detect_concepts_use_case: Any = None
    ) -> None:
        self.git_adapter = git_adapter
        self.file_scanner = file_scanner
        self.parser = parser
        self.entity_extractor = entity_extractor
        self.relationship_extractor = relationship_extractor
        self.diff_engine = diff_engine
        self.uow_factory = uow_factory
        self.identity_service = identity_service
        self.reconstruction_service = reconstruction_service
        self.logic_orchestrator = logic_orchestrator
        self.detect_concepts_use_case = detect_concepts_use_case

    def execute(self, repository_id: uuid.UUID | str, branch: str = "main", snapshot_interval: int = 100) -> dict:
        """Walks the commit history and ingests the repository temporally."""
        if isinstance(repository_id, str):
            repo_id = RepositoryId(uuid.UUID(repository_id))
        else:
            repo_id = RepositoryId(repository_id)
        
        # 1. Retrieve the repository
        with self.uow_factory() as uow:
            repo = uow.repositories.get_by_id(repo_id)
            if not repo:
                raise ValueError(f"Repository {repository_id} not found.")
            local_path = repo.local_path
            if not local_path:
                raise ValueError("Repository local path is missing. Ingestion must clone the repository first.")
            start_commit = repo.metadata.get("last_analyzed_commit")

        # 2. Clear existing static data if starting chronological walk from scratch
        if not start_commit:
            logger.info(f"Clearing existing static data for repository {repo_id} to perform chronological walk...")
            with self.uow_factory() as uow:
                # To be database agnostic (Postgres/SQLite) and bypass hyphen differences:
                # We use SQLAlchemy's model-based deletes instead of raw SQL strings.
                from sqlalchemy import delete, select
                from src.infrastructure.persistence.models import (
                    RepositorySnapshotModel,
                    CommitModel,
                    BenchmarkReportModel,
                    ChangeEventModel,
                    RelationshipVersionModel,
                    EntityVersionModel,
                    RelationshipModel,
                    CodeEntityModel,
                    AccuracyReportModel,
                    # Phase 3 models
                    LogicSignatureModel,
                    LogicVersionModel,
                    LogicEvidenceModel,
                    LogicTransitionModel,
                    BehaviorExplanationModel,
                    BehaviorDriftModel,
                    LogicClusterMemberModel,
                    LogicVersionPatternModel,
                )

                # Clear Phase 3 tables first (due to FK constraints and cascade deletions)
                sig_ids_subq = select(LogicSignatureModel.id).where(LogicSignatureModel.repository_id == repo_id.value)
                ver_ids_subq = select(LogicVersionModel.id).where(LogicVersionModel.signature_id.in_(sig_ids_subq))
                trans_ids_subq = select(LogicTransitionModel.id).where(
                    (LogicTransitionModel.from_version_id.in_(ver_ids_subq)) |
                    (LogicTransitionModel.to_version_id.in_(ver_ids_subq))
                )

                uow._session.execute(delete(LogicVersionPatternModel).where(LogicVersionPatternModel.version_id.in_(ver_ids_subq)))
                uow._session.execute(delete(LogicEvidenceModel).where(LogicEvidenceModel.version_id.in_(ver_ids_subq)))
                uow._session.execute(delete(BehaviorExplanationModel).where(BehaviorExplanationModel.version_id.in_(ver_ids_subq)))
                uow._session.execute(delete(BehaviorDriftModel).where(BehaviorDriftModel.transition_id.in_(trans_ids_subq)))
                uow._session.execute(delete(LogicTransitionModel).where(
                    (LogicTransitionModel.from_version_id.in_(ver_ids_subq)) |
                    (LogicTransitionModel.to_version_id.in_(ver_ids_subq))
                ))
                uow._session.execute(delete(LogicVersionModel).where(LogicVersionModel.signature_id.in_(sig_ids_subq)))
                uow._session.execute(delete(LogicClusterMemberModel).where(LogicClusterMemberModel.signature_id.in_(sig_ids_subq)))
                uow._session.execute(delete(LogicSignatureModel).where(LogicSignatureModel.repository_id == repo_id.value))

                # Clear Phase 1 and 2 tables
                uow._session.execute(delete(RepositorySnapshotModel).where(RepositorySnapshotModel.repository_id == repo_id.value))
                uow._session.execute(delete(BenchmarkReportModel).where(BenchmarkReportModel.repository_id == repo_id.value))
                uow._session.execute(delete(AccuracyReportModel).where(AccuracyReportModel.repository_id == repo_id.value))
                uow._session.execute(delete(ChangeEventModel).where(ChangeEventModel.repository_id == repo_id.value))

                rel_ids_subq = select(RelationshipModel.id).where(RelationshipModel.repository_id == repo_id.value)
                uow._session.execute(delete(RelationshipVersionModel).where(RelationshipVersionModel.relationship_id.in_(rel_ids_subq)))

                entity_seids_subq = select(CodeEntityModel.seid).where(CodeEntityModel.repository_id == repo_id.value)
                uow._session.execute(delete(EntityVersionModel).where(EntityVersionModel.seid.in_(entity_seids_subq)))

                uow._session.execute(delete(CommitModel).where(CommitModel.repository_id == repo_id.value))
                
                # Delete relationships, code_entities, source_files
                uow.relationships.delete_by_repository(repo_id)
                uow.code_entities.delete_by_repository(repo_id)
                uow.source_files.delete_by_repository(repo_id)
                uow.commit()


        # 3. Load existing source files (will be empty if cleared)
        with self.uow_factory() as uow:
            existing_files = uow.source_files.get_by_repository(repo_id)
            file_cache = {f.file_path: f for f in existing_files}

        logger.info(f"Starting history scan for repository {repo.name} starting from commit {start_commit}")

        # 2. Walk history
        walker = CommitWalker(local_path)
        commits_and_changes = walker.walk_history(repo_id, branch, start_commit)
        if not commits_and_changes:
            logger.info("No new commits to process.")
            return {"status": "success", "processed_commits": 0}

        processed_count = 0
        try:
            for commit_idx, (commit_entity, file_changes) in enumerate(commits_and_changes):
                commit_hash = commit_entity.hash
                logger.info(f"Processing commit {commit_hash} ({commit_idx + 1}/{len(commits_and_changes)})")

                t_commit_start = time.perf_counter()
                mem_start = get_memory_rss_bytes()

                # Checkout the commit
                self.git_adapter.checkout_commit(local_path, commit_hash)

                # Extract Graph B (current state at this commit)
                current_files = self.file_scanner.scan_repository(local_path)
                current_entities = []
                current_relationships = []
                files_to_save = []

                # Parse files and extract entities/relationships
                for scanned in current_files:
                    try:
                        with open(scanned.absolute_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        content_hash = self.identity_service.compute_content_hash(content)
                        
                        existing_file = file_cache.get(scanned.path)
                        if existing_file:
                            source_file = SourceFile(
                                id=existing_file.id,
                                repository_id=repo_id,
                                file_path=scanned.path,
                                language=scanned.language,
                                content_hash=content_hash,
                                line_count=len(content.splitlines()),
                                size_bytes=scanned.size_bytes
                            )
                            if existing_file.content_hash != content_hash or existing_file.size_bytes != scanned.size_bytes:
                                files_to_save.append(source_file)
                                file_cache[scanned.path] = source_file
                        else:
                            source_file = SourceFile(
                                id=FileId(uuid.uuid4()),
                                repository_id=repo_id,
                                file_path=scanned.path,
                                language=scanned.language,
                                content_hash=content_hash,
                                line_count=len(content.splitlines()),
                                size_bytes=scanned.size_bytes
                            )
                            files_to_save.append(source_file)
                            file_cache[scanned.path] = source_file

                        parse_result = self.parser.parse_file(scanned.absolute_path, content, scanned.language)
                        
                        file_entities = self.entity_extractor.extract(
                            parsed_tree=parse_result.tree,
                            source_code=content,
                            source_file=source_file,
                            repository_id=repo_id
                        )
                        current_entities.extend(file_entities)
                        
                        file_relationships = self.relationship_extractor.extract(
                            parsed_tree=parse_result.tree,
                            source_code=content,
                            entities=file_entities,
                            source_file=source_file
                        )
                        current_relationships.extend(file_relationships)

                    except Exception as fe:
                        logger.error(f"Error parsing file {scanned.path} in commit {commit_hash}: {fe}")

                # Retrieve Graph A (active database state before this commit)
                # This corresponds to the active entities and active relationships in the DB.
                # Since we process commits in chronological order, the database currently represents C_{n-1} state.
                with self.uow_factory() as uow:
                    previous_entities = uow.code_entities.get_by_repository(repo_id)
                    previous_relationships = uow.relationships.get_by_repository(repo_id)

                # Compute temporal diff
                t_diff_start = time.perf_counter()
                diff_result = self.diff_engine.compute_diff(
                    repo_id,
                    commit_hash,
                    previous_entities,
                    previous_relationships,
                    current_entities,
                    current_relationships,
                    file_changes
                )
                t_diff_duration = time.perf_counter() - t_diff_start

                # Persist the diff results in a single transaction
                with self.uow_factory() as uow:
                    # Save commit
                    uow.commits.save(commit_entity)

                    # Save source files
                    if files_to_save:
                        uow.source_files.save_batch(files_to_save)

                    # Save entities and versions
                    uow.code_entities.save_batch(diff_result.entities_to_save)
                    uow.entity_versions.save_batch(diff_result.versions_to_save)

                    # Save relationships and versions
                    uow.relationships.save_batch(diff_result.relationships_to_save)
                    uow.relationship_versions.save_batch(diff_result.relationship_versions_to_save)

                    # Save change events
                    uow.change_events.save_batch(diff_result.change_events_to_save)

                    # Periodic snapshot checkpointing
                    if commit_idx % snapshot_interval == 0:
                        # Collect active entity SEIDs and relationship IDs
                        active_seids = [e.seid for e in diff_result.entities_to_save if not e.metadata.get("is_deleted", False)]
                        active_rel_ids = [r.id for r in diff_result.relationships_to_save if not r.metadata.get("is_deleted", False)]
                        
                        snapshot_data = {
                            "entities": [{"seid": str(seid)} for seid in active_seids],
                            "relationships": [{"id": str(rid)} for rid in active_rel_ids]
                        }
                        
                        snapshot_entity = RepositorySnapshot(
                            id=uuid.uuid4(),
                            repository_id=repo_id,
                            commit_hash=commit_hash,
                            entity_seids=active_seids,
                            snapshot_data=snapshot_data,
                            created_at=datetime.datetime.now(datetime.timezone.utc)
                        )
                        uow.snapshots.save(snapshot_entity)

                    # Update Repository metadata
                    repo_db = uow.repositories.get_by_id(repo_id)
                    if repo_db:
                        repo_db.metadata["last_analyzed_commit"] = commit_hash
                        uow.repositories.save(repo_db)

                    uow.commit()

                # Run Phase 3 logic extraction hook
                if self.logic_orchestrator:
                    try:
                        self.logic_orchestrator.extract_repository_logic(repo_id, commit_hash)
                    except Exception as le:
                        logger.error(f"Error extracting logic for commit {commit_hash}: {le}", exc_info=True)

                # Run Phase 4 concept detection hook
                if self.detect_concepts_use_case:
                    try:
                        self.detect_concepts_use_case.execute(repo_id.value, commit_hash)
                    except Exception as ce:
                        logger.error(f"Error executing concept detection for commit {commit_hash}: {ce}", exc_info=True)

                # Post-commit benchmark telemetry collection
                try:
                    total_nodes = len(current_entities)
                    diff_throughput = 0.0
                    if t_diff_duration > 0:
                        diff_throughput = total_nodes / t_diff_duration

                    recon_latency_ms = 0
                    if self.reconstruction_service:
                        recon_start = time.perf_counter()
                        with self.uow_factory() as uow_recon:
                            self.reconstruction_service.reconstruct_graph_at_commit(
                                uow_recon, repo_id, commit_hash
                            )
                        recon_latency_ms = int((time.perf_counter() - recon_start) * 1000)

                    db_size = 0
                    with self.uow_factory() as uow_db:
                        db_size = get_db_size_bytes(uow_db._session)

                    mem_end = get_memory_rss_bytes()
                    max_mem_rss = max(mem_start, mem_end)

                    scan_duration_ms = int((time.perf_counter() - t_commit_start) * 1000)

                    benchmark = BenchmarkReport(
                        id=uuid.uuid4(),
                        repository_id=repo_id,
                        commit_hash=commit_hash,
                        scan_duration_ms=scan_duration_ms,
                        diff_throughput_nodes_sec=diff_throughput,
                        reconstruction_latency_ms=recon_latency_ms,
                        db_size_bytes=db_size,
                        memory_rss_bytes=max_mem_rss,
                        measured_at=datetime.datetime.now(datetime.timezone.utc)
                    )
                    with self.uow_factory() as uow_bench:
                        uow_bench.metrics.save_benchmark_report(benchmark)
                        uow_bench.commit()
                except Exception as telemetry_error:
                    logger.warning(f"Error collecting benchmark metrics: {telemetry_error}", exc_info=True)
                
                processed_count += 0.5 # use float to accumulate or int
                processed_count = int(processed_count + 0.5)

            # Update Repository status to completed
            with self.uow_factory() as uow:
                repo_db = uow.repositories.get_by_id(repo_id)
                if repo_db:
                    repo_db.status = AnalysisStatus.COMPLETED
                    uow.repositories.save(repo_db)
                    uow.commit()

        finally:
            # Checkout default branch back to ensure workspace is clean
            try:
                self.git_adapter.checkout_commit(local_path, branch)
            except Exception as checkout_error:
                logger.error(f"Failed to reset repository branch to {branch} after walk: {checkout_error}")

        return {"status": "success", "processed_commits": processed_count}
