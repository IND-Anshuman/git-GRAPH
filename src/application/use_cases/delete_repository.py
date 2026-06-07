import os
import shutil
import uuid
import logging
from typing import Callable

from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.exceptions import RepositoryNotFoundException
from src.domain.value_objects.repository_id import RepositoryId

logger = logging.getLogger(__name__)


class DeleteRepositoryUseCase:
    """Handles the business logic for deleting an ingested repository and cleaning up local folders."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]):
        self.uow_factory = uow_factory

    def execute(self, repository_id: str) -> bool:
        """Deletes repository metadata and its cloned repository directory from disk."""
        try:
            repo_uuid = uuid.UUID(repository_id)
        except ValueError:
            raise RepositoryNotFoundException(f"Invalid repository ID format: {repository_id}")

        with self.uow_factory() as uow:
            repo = uow.repositories.get_by_id(RepositoryId(repo_uuid))
            if not repo:
                raise RepositoryNotFoundException(f"Repository {repository_id} not found")

            # Clean up local cloned repository files on disk
            local_path = repo.local_path
            if local_path and os.path.exists(local_path):
                logger.info(f"Cleaning up local cloned repository folder: {local_path}")
                try:
                    # Helper function to remove read-only attributes on Windows
                    def onerror(func, path, exc_info):
                        import stat
                        if not os.access(path, os.W_OK):
                            os.chmod(path, stat.S_IWUSR)
                            func(path)
                        else:
                            raise
                    shutil.rmtree(local_path, onerror=onerror)
                    logger.info("Local clone folder cleaned up successfully.")
                except Exception as e:
                    logger.warning(f"Could not clean up local clone path {local_path}: {e}")

            # Delete repository from database
            uow.repositories.delete(RepositoryId(repo_uuid))
            uow.commit()
            return True
