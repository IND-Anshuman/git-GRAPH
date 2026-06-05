"""Abstract repository interface for BehaviorDrift persistence operations."""

from abc import ABC, abstractmethod
from typing import Any
import uuid

from src.domain.entities.behavior_drift import BehaviorDrift
from src.domain.enums.drift_category import DriftCategory
from src.domain.value_objects.repository_id import RepositoryId


class IBehaviorDriftRepository(ABC):
    """Port defining persistence operations for BehaviorDrift domain entities."""

    @abstractmethod
    def save(self, drift: BehaviorDrift) -> None:
        """
        Persist a single BehaviorDrift record, inserting or updating as appropriate.

        Args:
            drift: The BehaviorDrift to save.
        """
        pass

    @abstractmethod
    def get_by_transition(
        self, logic_transition_id: uuid.UUID
    ) -> BehaviorDrift | None:
        """
        Return the BehaviorDrift associated with a specific LogicTransition.

        Args:
            logic_transition_id: The UUID of the LogicTransition.

        Returns:
            The associated BehaviorDrift, or None if not computed.
        """
        pass

    @abstractmethod
    def list_by_security_boundary_crossed(
        self, repository_id: RepositoryId
    ) -> list[BehaviorDrift]:
        """
        Return all BehaviorDrift records where a security boundary was crossed,
        scoped to a repository.

        Args:
            repository_id: The repository to scope the query.

        Returns:
            A list of security-boundary-crossing BehaviorDrift records.
        """
        pass

    @abstractmethod
    def list_by_drift_category(
        self, repository_id: RepositoryId, category: DriftCategory
    ) -> list[BehaviorDrift]:
        """
        Return all BehaviorDrift records with a given drift category for a repository.

        Args:
            repository_id: The repository to scope the query.
            category: The DriftCategory to filter by.

        Returns:
            A list of BehaviorDrift records matching the category.
        """
        pass

    @abstractmethod
    def get_drift_summary(self, repository_id: RepositoryId) -> dict[str, Any]:
        """
        Compute an aggregated drift summary for a repository.

        The summary typically includes counts per DriftCategory, average drift
        score, and security-crossing count.

        Args:
            repository_id: The repository to summarize.

        Returns:
            A dict containing summary statistics.
        """
        pass
