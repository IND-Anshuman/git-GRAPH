"""Abstract repository interface for BehaviorExplanation persistence operations."""

from abc import ABC, abstractmethod
import uuid

from src.domain.entities.behavior_explanation import BehaviorExplanation


class ILogicExplanationRepository(ABC):
    """Port defining persistence operations for BehaviorExplanation domain entities."""

    @abstractmethod
    def save(self, explanation: BehaviorExplanation) -> None:
        """
        Persist a single BehaviorExplanation, inserting or updating as appropriate.

        Args:
            explanation: The BehaviorExplanation to save.
        """
        pass

    @abstractmethod
    def get_by_logic_version(
        self, logic_version_id: uuid.UUID
    ) -> BehaviorExplanation | None:
        """
        Return the explanation attached to a specific LogicVersion.

        Args:
            logic_version_id: The UUID of the LogicVersion.

        Returns:
            The associated BehaviorExplanation, or None if not yet generated.
        """
        pass

    @abstractmethod
    def list_by_behavior_name(self, behavior_name: str) -> list[BehaviorExplanation]:
        """
        Return all BehaviorExplanations with a given behavior_name.

        Args:
            behavior_name: The behavior display name to filter by.

        Returns:
            A list of matching BehaviorExplanation objects.
        """
        pass

    @abstractmethod
    def list_by_ontology_path(self, ontology_path: str) -> list[BehaviorExplanation]:
        """
        Return all BehaviorExplanations referencing a specific ontology path.

        Args:
            ontology_path: The dot-path ontology node ID to filter by.

        Returns:
            A list of matching BehaviorExplanation objects.
        """
        pass

    @abstractmethod
    def mark_stale_by_pattern(self, pattern_id: str) -> int:
        """
        Mark as stale all BehaviorExplanations that reference a given pattern ID.

        Called when a BehaviorPattern definition is reloaded from YAML so that
        outdated explanations are flagged for regeneration.

        Args:
            pattern_id: The pattern identifier whose explanations should be staled.

        Returns:
            The number of BehaviorExplanation records marked stale.
        """
        pass
