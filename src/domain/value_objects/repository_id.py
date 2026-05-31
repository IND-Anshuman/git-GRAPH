from dataclasses import dataclass
import uuid

@dataclass(frozen=True)
class RepositoryId:
    """Identifier for a Repository."""
    value: uuid.UUID

    @classmethod
    def generate(cls) -> "RepositoryId":
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> "RepositoryId":
        return cls(value=uuid.UUID(id_str))

    def __str__(self) -> str:
        return str(self.value)
