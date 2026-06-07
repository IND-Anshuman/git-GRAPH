"""Service for executing historical concept backfills over existing repositories."""

import uuid
import logging
from typing import Callable, Any
from sqlalchemy import delete, select

from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId
from src.infrastructure.persistence.models.concept_models import (
    ConceptNodeModel,
    ConceptVersionModel,
    ConceptEvidenceModel,
    ConceptRelationshipModel,
    ConceptExplanationModel,
    ConceptMetricsModel,
    ConceptDriftModel,
    ConceptEvolutionModel,
)

logger = logging.getLogger(__name__)


class ConceptBackfillService:
    """Orchestrates retroactive execution of Phase 4 concept detection over full history."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork], detect_concepts_use_case: Any = None) -> None:
        self.uow_factory = uow_factory
        # detect_concepts_use_case is typed as Any to avoid circular import issues in DI container
        self.detect_concepts_use_case = detect_concepts_use_case

    def backfill_repository(self, repository_id: uuid.UUID) -> dict:
        """
        Walks the repository's commit history chronologically, running concept detection at each step.

        Args:
            repository_id: The UUID of the target repository.

        Returns:
            A status dictionary detailing the number of commits backfilled.
        """
        repo_id = RepositoryId(repository_id)

        # 1. Verify repository exists and load commits
        with self.uow_factory() as uow:
            repo = uow.repositories.get_by_id(repo_id)
            if not repo:
                raise ValueError(f"Repository {repository_id} not found.")

            commits = uow.commits.list_by_repository(repo_id)
            if not commits:
                logger.info(f"No commits found in database for repository {repository_id}.")
                return {"status": "success", "processed_commits": 0}

            # Sort commits chronologically by timestamp ascending
            commits.sort(key=lambda c: c.timestamp)

        logger.info(f"Starting historical concept backfill for repository {repo.name} ({len(commits)} commits)...")

        # 2. Clear existing concept data for this repository to avoid duplicate keys/inconsistencies
        with self.uow_factory() as uow:
            node_ids_subq = select(ConceptNodeModel.id).where(ConceptNodeModel.repository_id == repository_id)
            ver_ids_subq = select(ConceptVersionModel.id).where(ConceptVersionModel.concept_id.in_(node_ids_subq))

            uow._session.execute(
                delete(ConceptEvolutionModel).where(
                    (ConceptEvolutionModel.from_concept_version_id.in_(ver_ids_subq))
                    | (ConceptEvolutionModel.to_concept_version_id.in_(ver_ids_subq))
                )
            )
            uow._session.execute(delete(ConceptDriftModel).where(ConceptDriftModel.concept_id.in_(node_ids_subq)))
            uow._session.execute(delete(ConceptMetricsModel).where(ConceptMetricsModel.concept_version_id.in_(ver_ids_subq)))
            uow._session.execute(delete(ConceptExplanationModel).where(ConceptExplanationModel.concept_version_id.in_(ver_ids_subq)))
            uow._session.execute(delete(ConceptEvidenceModel).where(ConceptEvidenceModel.concept_version_id.in_(ver_ids_subq)))
            uow._session.execute(delete(ConceptRelationshipModel).where(ConceptRelationshipModel.repository_id == repository_id))
            uow._session.execute(delete(ConceptVersionModel).where(ConceptVersionModel.concept_id.in_(node_ids_subq)))
            uow._session.execute(delete(ConceptNodeModel).where(ConceptNodeModel.repository_id == repository_id))
            uow.commit()

        # 3. Iteratively execute the concept detection use case
        processed_count = 0
        for commit in commits:
            logger.info(f"Backfilling concepts for commit {commit.hash} ({commit.timestamp})")
            try:
                self.detect_concepts_use_case.execute(repository_id, commit.hash)
                processed_count += 1
            except Exception as e:
                logger.error(f"Failed to backfill concepts for commit {commit.hash}: {e}", exc_info=True)
                raise

        logger.info(f"Successfully backfilled {processed_count} commits for repository {repo.name}.")
        return {"status": "success", "processed_commits": processed_count}
