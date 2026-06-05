"""Abstract repository interface for LogicCluster persistence operations."""

from abc import ABC, abstractmethod
import uuid

from src.domain.entities.logic_cluster import LogicCluster


class ILogicClusterRepository(ABC):
    """Port defining persistence operations for LogicCluster domain entities."""

    @abstractmethod
    def save(self, cluster: LogicCluster) -> None:
        """
        Persist a single LogicCluster, inserting or updating as appropriate.

        Args:
            cluster: The LogicCluster to save.
        """
        pass

    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> LogicCluster | None:
        """
        Retrieve a LogicCluster by its primary key.

        Args:
            id: The UUID of the LogicCluster.

        Returns:
            The matching LogicCluster, or None if not found.
        """
        pass

    @abstractmethod
    def list_all(self) -> list[LogicCluster]:
        """
        Return all LogicClusters.

        Returns:
            A list of all LogicCluster objects.
        """
        pass

    @abstractmethod
    def add_member(self, cluster_id: uuid.UUID, signature_id: uuid.UUID) -> None:
        """
        Add a LogicSignature as a member of a cluster.

        Args:
            cluster_id: The UUID of the LogicCluster.
            signature_id: The UUID of the LogicSignature.
        """
        pass

    @abstractmethod
    def remove_member(self, cluster_id: uuid.UUID, signature_id: uuid.UUID) -> None:
        """
        Remove a LogicSignature membership from a cluster.

        Args:
            cluster_id: The UUID of the LogicCluster.
            signature_id: The UUID of the LogicSignature.
        """
        pass
