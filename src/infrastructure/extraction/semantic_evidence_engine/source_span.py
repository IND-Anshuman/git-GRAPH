from dataclasses import dataclass

@dataclass(frozen=True)
class SourceSpan:
    """Represents a range of text in a source file."""
    file_path: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    start_byte: int
    end_byte: int
