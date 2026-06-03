from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

from src.domain.entities.integrity import IntegrityViolation, RepairAudit
from src.domain.value_objects.repository_id import RepositoryId

class IIntegrityRepository(ABC):
    """Abstract port for managing validation violations and audits."""

    @abstractmethod
    def save_violation(self, violation: IntegrityViolation) -> None:
        """Save a structural validation integrity issue."""
        pass

    @abstractmethod
    def save_violations_batch(self, violations: List[IntegrityViolation]) -> None:
        """Save multiple integrity issues in bulk."""
        pass

    @abstractmethod
    def get_violation_by_id(self, violation_id: uuid.UUID) -> Optional[IntegrityViolation]:
        """Fetch a specific integrity violation by its ID."""
        pass

    @abstractmethod
    def list_violations_by_repository(self, repo_id: RepositoryId, unresolved_only: bool = False) -> List[IntegrityViolation]:
        """Retrieve all registered validation issues for a repository."""
        pass

    @abstractmethod
    def save_repair_audit(self, audit: RepairAudit) -> None:
        """Save a repair execution log."""
        pass

    @abstractmethod
    def list_repair_audits_by_repository(self, repo_id: RepositoryId) -> List[RepairAudit]:
        """Retrieve all structural repair operations done on a repository."""
        pass
