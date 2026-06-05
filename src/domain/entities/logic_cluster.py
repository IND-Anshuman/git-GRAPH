"""Domain entity representing a cluster of related logic signatures."""

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LogicCluster:
    """
    A LogicCluster groups semantically related LogicSignatures so that cross-cutting
    queries (e.g., "show all authentication patterns") can be answered efficiently.

    Cluster membership is mutable: signatures can be added or removed as the
    analysis pipeline evolves.
    """

    id: uuid.UUID
    """Unique identifier for this cluster."""

    name: str
    """Human-readable cluster name (e.g., 'Authentication Patterns')."""

    category: str
    """High-level category label (e.g., 'Security', 'DataAccess', 'Serialization')."""

    logic_signature_ids: list[uuid.UUID] = field(default_factory=list)
    """Ordered list of LogicSignature IDs that belong to this cluster."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Arbitrary extensible metadata."""

    def add_signature(self, sig_id: uuid.UUID) -> None:
        """
        Add a LogicSignature to this cluster if not already present.

        Args:
            sig_id: The UUID of the LogicSignature to add.
        """
        if sig_id not in self.logic_signature_ids:
            self.logic_signature_ids.append(sig_id)

    def remove_signature(self, sig_id: uuid.UUID) -> None:
        """
        Remove a LogicSignature from this cluster.

        Args:
            sig_id: The UUID of the LogicSignature to remove.
        """
        self.logic_signature_ids = [
            sid for sid in self.logic_signature_ids if sid != sig_id
        ]

    def contains(self, sig_id: uuid.UUID) -> bool:
        """
        Check whether a LogicSignature is a member of this cluster.

        Args:
            sig_id: The UUID of the LogicSignature to check.

        Returns:
            True if the signature is in this cluster.
        """
        return sig_id in self.logic_signature_ids
