"""Use case for scanning repository Git history and populating the temporal graph."""

import datetime
import logging
import uuid
from typing import Any, Callable, List

from src.application.ports.git_port import IGitAdapter
from src.application.ports.file_scanner_port import IFileScanner
from src.application.ports.parser_port import IParser
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.entities.repository_snapshot import RepositorySnapshot
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.file_id import FileId
from src.domain.entities.source_file import SourceFile
from src.infrastructure.git.commit_walker import CommitWalker
from src.infrastructure.git.temporal_diff_engine import TemporalDiffEngine

logger = logging.getLogger(__name__)

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
        identity_service: Any
    ) -> None:
        self.git_adapter = git_adapter
        self.file_scanner = file_scanner
        self.parser = parser
        self.entity_extractor = entity_extractor
        self.relationship_extractor = relationship_extractor
        self.diff_engine = diff_engine
        self.uow_factory = uow_factory
        self.identity_service = identity_service

    def execute(self, repository_id: uuid.UUID, branch: str = "main", snapshot_interval: int = 100) -> dict:
        """Walks the commit history and ingests the repository temporally."""
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

                # Checkout the commit
                self.git_adapter.checkout_commit(local_path, commit_hash)

                # Extract Graph B (current state at this commit)
                current_files = self.file_scanner.scan_repository(local_path)
                current_entities = []
                current_relationships = []

                # Parse files and extract entities/relationships
                for scanned in current_files:
                    try:
                        with open(scanned.absolute_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        content_hash = self.identity_service.compute_content_hash(content)
                        source_file = SourceFile(
                            id=FileId(uuid.uuid4()),
                            repository_id=repo_id,
                            file_path=scanned.path,
                            language=scanned.language,
                            content_hash=content_hash,
                            line_count=len(content.splitlines()),
                            size_bytes=scanned.size_bytes
                        )

                        parse_result = self.parser.parse_file(scanned.absolute_path, content, scanned.language)
                        
                        file_entities = self.entity_extractor.extract(
                            parse_result.tree, source_file, content
                        )
                        current_entities.extend(file_entities)
                        
                        file_relationships = self.relationship_extractor.extract(
                            parse_result.tree, file_entities, source_file, content
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
                diff_result = self.diff_engine.compute_diff(
                    repo_id,
                    commit_hash,
                    previous_entities,
                    previous_relationships,
                    current_entities,
                    current_relationships,
                    file_changes
                )

                # Persist the diff results in a single transaction
                with self.uow_factory() as uow:
                    # Save commit
                    uow.commits.save(commit_entity)

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
