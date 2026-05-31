from dataclasses import dataclass
import uuid

@dataclass(frozen=True)
class FileId:
    """Identifier for a SourceFile."""
    value: uuid.UUID

    @classmethod
    def generate(cls) -> "FileId":
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> "FileId":
        return cls(value=uuid.UUID(id_str))

    def __str__(self) -> str:
        return str(self.value)
