"""Abstract repository interface for LogicTransition persistence operations."""

from abc import ABC, abstractmethod
import uuid

from src.domain.entities.logic_transition import LogicTransition


class ILogicTransitionRepository(ABC):
    """Port defining persistence operations for LogicTransition domain entities."""

    @abstractmethod
    def save(self, transition: LogicTransition) -> None:
        """
        Persist a single LogicTransition, inserting or updating as appropriate.

        Args:
            transition: The LogicTransition to save.
        """
        pass

    @abstractmethod
    def save_batch(self, transitions: list[LogicTransition]) -> None:
        """
        Persist multiple LogicTransitions in a single batch operation.

        Args:
            transitions: The list of LogicTransitions to save.
        """
        pass

    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> LogicTransition | None:
        """
        Retrieve a LogicTransition by its primary key.

        Args:
            id: The UUID of the LogicTransition.

        Returns:
            The matching LogicTransition, or None if not found.
        """
        pass

    @abstractmethod
    def get_by_from_version(
        self, from_version_id: uuid.UUID
    ) -> list[LogicTransition]:
        """
        Return all LogicTransitions that originate from a given LogicVersion.

        Args:
            from_version_id: The source LogicVersion UUID.

        Returns:
            A list of outbound LogicTransition objects.
        """
        pass

    @abstractmethod
    def get_by_to_version(self, to_version_id: uuid.UUID) -> list[LogicTransition]:
        """
        Return all LogicTransitions that target a given LogicVersion.

        Args:
            to_version_id: The destination LogicVersion UUID.

        Returns:
            A list of inbound LogicTransition objects.
        """
        pass

    @abstractmethod
    def list_by_signature(
        self, logic_signature_id: uuid.UUID
    ) -> list[LogicTransition]:
        """
        Return all LogicTransitions in the evolution chain of a LogicSignature.

        Args:
            logic_signature_id: The parent LogicSignature UUID.

        Returns:
            A list of LogicTransition objects for the full history.
        """
        pass
