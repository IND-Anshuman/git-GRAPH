"""Abstract repository interface for BehaviorPattern persistence operations."""

from abc import ABC, abstractmethod

from src.domain.entities.behavior_pattern import BehaviorPattern


class IBehaviorPatternRepository(ABC):
    """Port defining persistence operations for BehaviorPattern domain entities."""

    @abstractmethod
    def save(self, pattern: BehaviorPattern) -> None:
        """
        Persist a single BehaviorPattern, inserting or updating as appropriate.

        Args:
            pattern: The BehaviorPattern to save.
        """
        pass

    @abstractmethod
    def save_batch(self, patterns: list[BehaviorPattern]) -> None:
        """
        Persist multiple BehaviorPatterns in a single batch operation.

        Args:
            patterns: The list of BehaviorPatterns to save.
        """
        pass

    @abstractmethod
    def get_by_pattern_id(self, pattern_id: str) -> BehaviorPattern | None:
        """
        Retrieve a BehaviorPattern by its pattern identifier.

        Args:
            pattern_id: The stable pattern identifier (e.g., 'auth_bcrypt_verification').

        Returns:
            The matching BehaviorPattern, or None if not found.
        """
        pass

    @abstractmethod
    def list_active(self) -> list[BehaviorPattern]:
        """
        Return all active BehaviorPatterns.

        Returns:
            A list of active BehaviorPattern objects.
        """
        pass

    @abstractmethod
    def list_by_ontology_node(self, ontology_node_id: str) -> list[BehaviorPattern]:
        """
        Return all BehaviorPatterns associated with a specific ontology node.

        Args:
            ontology_node_id: The dot-path ID of the ontology node.

        Returns:
            A list of BehaviorPattern objects.
        """
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """
        Delete all loaded BehaviorPatterns.

        Used when reloading patterns from the YAML catalog.
        """
        pass
