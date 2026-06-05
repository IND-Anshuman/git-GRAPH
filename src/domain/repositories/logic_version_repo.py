"""Abstract repository interface for LogicVersion persistence operations."""

from abc import ABC, abstractmethod
import uuid

from src.domain.entities.logic_version import LogicVersion
from src.domain.value_objects.entity_id import SEID


class ILogicVersionRepository(ABC):
    """Port defining persistence operations for LogicVersion domain entities."""

    @abstractmethod
    def save(self, version: LogicVersion) -> None:
        """
        Persist a single LogicVersion, inserting or updating as appropriate.

        Args:
            version: The LogicVersion to save.
        """
        pass

    @abstractmethod
    def save_batch(self, versions: list[LogicVersion]) -> None:
        """
        Persist multiple LogicVersions in a single batch operation.

        Args:
            versions: The list of LogicVersions to save.
        """
        pass

    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> LogicVersion | None:
        """
        Retrieve a LogicVersion by its primary key.

        Args:
            id: The UUID of the LogicVersion.

        Returns:
            The matching LogicVersion, or None if not found.
        """
        pass

    @abstractmethod
    def get_by_entity_at_commit(
        self, seid: SEID, commit_hash: str
    ) -> list[LogicVersion]:
        """
        Return all LogicVersions detected for a code entity at a specific commit.

        Args:
            seid: The stable entity identifier.
            commit_hash: The VCS commit hash.

        Returns:
            A list of LogicVersion objects (may contain multiple candidates).
        """
        pass

    @abstractmethod
    def get_primary_by_entity_at_commit(
        self, seid: SEID, commit_hash: str
    ) -> LogicVersion | None:
        """
        Return the primary (canonical) LogicVersion for a code entity at a commit.

        Args:
            seid: The stable entity identifier.
            commit_hash: The VCS commit hash.

        Returns:
            The primary LogicVersion, or None if none exists.
        """
        pass

    @abstractmethod
    def list_by_signature(self, logic_signature_id: uuid.UUID) -> list[LogicVersion]:
        """
        Return all LogicVersions attached to a given LogicSignature.

        Args:
            logic_signature_id: The parent LogicSignature UUID.

        Returns:
            A list of LogicVersion objects.
        """
        pass

    @abstractmethod
    def list_by_entity_timeline(self, seid: SEID) -> list[LogicVersion]:
        """
        Return all LogicVersions for a code entity ordered chronologically.

        Args:
            seid: The stable entity identifier.

        Returns:
            A chronologically ordered list of LogicVersion objects.
        """
        pass

    @abstractmethod
    def get_previous_versions(
        self, seid: SEID, commit_hash: str
    ) -> list[LogicVersion]:
        """
        Return LogicVersions for a code entity that predate the given commit.

        Args:
            seid: The stable entity identifier.
            commit_hash: The reference commit hash.

        Returns:
            A list of LogicVersions recorded before the given commit.
        """
        pass
