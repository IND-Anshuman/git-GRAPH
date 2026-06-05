"""Abstract repository interface for LogicEvidence persistence operations."""

from abc import ABC, abstractmethod
import uuid

from src.domain.entities.logic_evidence import LogicEvidence
from src.domain.enums.evidence_type import EvidenceType


class ILogicEvidenceRepository(ABC):
    """Port defining persistence operations for LogicEvidence domain entities."""

    @abstractmethod
    def save_batch(self, evidence: list[LogicEvidence]) -> None:
        """
        Persist a batch of LogicEvidence records in a single operation.

        Evidence is always written in bulk after a detection pass completes.

        Args:
            evidence: The list of LogicEvidence items to save.
        """
        pass

    @abstractmethod
    def get_by_logic_version(self, logic_version_id: uuid.UUID) -> list[LogicEvidence]:
        """
        Return all LogicEvidence records associated with a LogicVersion.

        Args:
            logic_version_id: The UUID of the parent LogicVersion.

        Returns:
            A list of LogicEvidence objects (may be empty).
        """
        pass

    @abstractmethod
    def get_by_evidence_type(
        self, logic_version_id: uuid.UUID, evidence_type: EvidenceType
    ) -> list[LogicEvidence]:
        """
        Return LogicEvidence records for a LogicVersion filtered by evidence type.

        Args:
            logic_version_id: The UUID of the parent LogicVersion.
            evidence_type: The category of evidence to filter by.

        Returns:
            A list of matching LogicEvidence objects.
        """
        pass

    @abstractmethod
    def delete_by_logic_version(self, logic_version_id: uuid.UUID) -> None:
        """
        Remove all evidence records associated with a LogicVersion.

        Used when a LogicVersion is regenerated and old evidence must be replaced.

        Args:
            logic_version_id: The UUID of the LogicVersion whose evidence to delete.
        """
        pass
