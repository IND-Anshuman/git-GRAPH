"""Abstract repository interface for OntologyNode persistence operations."""

from abc import ABC, abstractmethod

from src.domain.entities.ontology_node import OntologyNode


class IOntologyNodeRepository(ABC):
    """Port defining persistence operations for OntologyNode domain entities."""

    @abstractmethod
    def save(self, node: OntologyNode) -> None:
        """
        Persist a single OntologyNode, inserting or updating as appropriate.

        Args:
            node: The OntologyNode to save.
        """
        pass

    @abstractmethod
    def save_batch(self, nodes: list[OntologyNode]) -> None:
        """
        Persist multiple OntologyNodes in a single batch operation.

        Args:
            nodes: The list of OntologyNodes to save.
        """
        pass

    @abstractmethod
    def get_by_id(self, node_id: str) -> OntologyNode | None:
        """
        Retrieve an OntologyNode by its dot-path identifier.

        Args:
            node_id: The unique dot-path identifier (e.g., 'security.authentication.hash_comparison').

        Returns:
            The matching OntologyNode, or None if not found.
        """
        pass

    @abstractmethod
    def list_by_domain(self, domain: str) -> list[OntologyNode]:
        """
        Return all OntologyNodes in a top-level domain.

        Args:
            domain: The top-level domain name (e.g., 'Security').

        Returns:
            A list of OntologyNode objects.
        """
        pass

    @abstractmethod
    def list_children(self, parent_id: str) -> list[OntologyNode]:
        """
        Return all child nodes for a given parent node.

        Args:
            parent_id: The parent dot-path identifier.

        Returns:
            A list of child OntologyNode objects.
        """
        pass

    @abstractmethod
    def list_all(self) -> list[OntologyNode]:
        """
        Return all OntologyNodes.

        Returns:
            A list of all OntologyNode objects.
        """
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """
        Delete all loaded OntologyNodes.

        Used when reloading ontology from the YAML catalog.
        """
        pass

    @abstractmethod
    def get_current_version(self) -> str | None:
        """
        Retrieve the latest loaded version of the ontology.

        Returns:
            The version string, or None if no nodes are loaded.
        """
        pass
