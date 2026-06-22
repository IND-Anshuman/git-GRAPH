"""Use case for triggering bulk logic extraction on all commits of a repository."""

from typing import Callable

from src.domain.value_objects.repository_id import RepositoryId
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.services.logic_extraction_orchestrator import (
    LogicExtractionOrchestrator,
)


class ExtractAllLogicUseCase:
    """Triggers behavioral logic extraction for all commits in a repository."""

    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        orchestrator: LogicExtractionOrchestrator,
    ) -> None:
        self.uow_factory = uow_factory
        self.orchestrator = orchestrator

    def execute(self, repository_id_str: str) -> bool:
        """
        Execute logic extraction for all commits in a repository.

        Returns True if successful.
        """
        repo_id = RepositoryId.from_string(repository_id_str)
        with self.uow_factory() as uow:
            # Check if repository exists
            repo = uow.repositories.get_by_id(repo_id)
            if not repo:
                return False

        # Run orchestrator logic extraction (which uses checkout and parsing)
        self.orchestrator.extract_all_repository_logic(repo_id)
        return True
