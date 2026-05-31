from dataclasses import dataclass
import uuid

@dataclass(frozen=True)
class SEID:
    """Stable Entity ID."""
    value: uuid.UUID

    @classmethod
    def generate(cls) -> "SEID":
        """Generate a new SEID with a random UUID."""
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> "SEID":
        """Create an SEID from a string."""
        return cls(value=uuid.UUID(id_str))

    def __str__(self) -> str:
        return str(self.value)
