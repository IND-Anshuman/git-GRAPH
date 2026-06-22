"""Use case for triggering all-in-one logic extraction and concept intelligence extraction for a repository."""

import uuid
from typing import Callable, Any
from src.domain.value_objects.repository_id import RepositoryId
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.services.logic_extraction_orchestrator import (
    LogicExtractionOrchestrator,
)
from src.application.services.concept_backfill_service import (
    ConceptBackfillService,
)

class ExtractAllInOneConceptsUseCase:
    """Executes behavioral logic extraction followed by concept detection (either repository-wide or for a specific commit)."""

    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        logic_orchestrator: LogicExtractionOrchestrator,
        concept_backfill_service: ConceptBackfillService,
        detect_concepts_use_case: Any,
    ) -> None:
        self.uow_factory = uow_factory
        self.logic_orchestrator = logic_orchestrator
        self.concept_backfill_service = concept_backfill_service
        self.detect_concepts_use_case = detect_concepts_use_case

    def execute(self, repository_id_str: str, commit_hash: str | None = None) -> dict:
        """
        Execute all-in-one logic and concept extraction.
        
        Returns a summary of the execution.
        """
        repo_uuid = uuid.UUID(repository_id_str)
        repo_id = RepositoryId(repo_uuid)

        # 1. Verify repository exists
        with self.uow_factory() as uow:
            repo = uow.repositories.get_by_id(repo_id)
            if not repo:
                raise ValueError(f"Repository {repository_id_str} not found.")

        if commit_hash:
            # Targeted extraction for a single commit
            print(f"[AllInOneConcepts] Extracting logic for commit {commit_hash}...")
            self.logic_orchestrator.extract_repository_logic(repo_id, commit_hash)
            
            print(f"[AllInOneConcepts] Detecting concepts for commit {commit_hash}...")
            detection_summary = self.detect_concepts_use_case.execute(repo_uuid, commit_hash)
            
            return {
                "status": "success",
                "message": f"All-in-one logic and concept extraction completed for commit {commit_hash}.",
                "commit_hash": commit_hash,
                "concepts_detected": detection_summary.get("concepts_detected", 0),
                "relationships_inferred": detection_summary.get("relationships_inferred", 0),
            }
        else:
            # Bulk repository-wide extraction
            print("[AllInOneConcepts] Running bulk logic extraction for all commits...")
            self.logic_orchestrator.extract_all_repository_logic(repo_id)
            
            print("[AllInOneConcepts] Running historical concept backfill...")
            backfill_summary = self.concept_backfill_service.backfill_repository(repo_uuid)
            
            return {
                "status": "success",
                "message": "All-in-one logic and concept extraction completed repository-wide.",
                "processed_commits": backfill_summary.get("processed_commits", 0),
            }
