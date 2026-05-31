from dataclasses import dataclass

@dataclass(frozen=True)
class CodeLocation:
    """Location of code within a file."""
    file_path: str
    start_line: int
    end_line: int
    start_column: int | None = None
    end_column: int | None = None
