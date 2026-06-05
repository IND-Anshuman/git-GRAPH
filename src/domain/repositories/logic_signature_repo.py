"""Abstract repository interface for LogicSignature persistence operations."""

from abc import ABC, abstractmethod
import uuid

from src.domain.entities.logic_signature import LogicSignature
from src.domain.value_objects.repository_id import RepositoryId


class ILogicSignatureRepository(ABC):
    """Port defining persistence operations for LogicSignature domain entities."""

    @abstractmethod
    def save(self, signature: LogicSignature) -> None:
        """
        Persist a single LogicSignature, inserting or updating as appropriate.

        Args:
            signature: The LogicSignature to save.
        """
        pass

    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> LogicSignature | None:
        """
        Retrieve a LogicSignature by its primary key.

        Args:
            id: The UUID of the LogicSignature.

        Returns:
            The matching LogicSignature, or None if not found.
        """
        pass

    @abstractmethod
    def get_by_canonical_name(
        self, repository_id: RepositoryId, name: str
    ) -> LogicSignature | None:
        """
        Retrieve a LogicSignature by its repository-scoped canonical name.

        Args:
            repository_id: The repository to search within.
            name: The canonical name to look up.

        Returns:
            The matching LogicSignature, or None if not found.
        """
        pass

    @abstractmethod
    def list_by_repository(self, repository_id: RepositoryId) -> list[LogicSignature]:
        """
        Return all LogicSignatures registered for a given repository.

        Args:
            repository_id: The target repository.

        Returns:
            A list of LogicSignature objects (may be empty).
        """
        pass

    @abstractmethod
    def list_by_ontology_node(self, ontology_node_id: str) -> list[LogicSignature]:
        """
        Return all LogicSignatures that reference a specific ontology node.

        Args:
            ontology_node_id: The dot-path ontology node ID to filter by.

        Returns:
            A list of matching LogicSignature objects.
        """
        pass

    @abstractmethod
    def delete_by_repository(self, repository_id: RepositoryId) -> None:
        """
        Remove all LogicSignatures belonging to a repository.

        Args:
            repository_id: The repository whose signatures should be deleted.
        """
        pass
