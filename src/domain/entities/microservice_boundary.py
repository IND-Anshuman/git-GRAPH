"""Domain entity representing a boundary separating distributed services."""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class MicroserviceBoundary:
    """Represents distributed runtime boundaries (e.g. REST calls, queues)."""

    id: uuid.UUID
    name: str
    boundary_type: str  # HTTP, GRPC, KAFKA, RABBITMQ, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validates invariants of the MicroserviceBoundary."""
        if not self.name or not self.name.strip():
            raise ValueError("MicroserviceBoundary.name must be specified.")
        if not self.boundary_type or not self.boundary_type.strip():
            raise ValueError("MicroserviceBoundary.boundary_type must be specified.")
