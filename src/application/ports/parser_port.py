from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from src.domain.enums import SupportedLanguage

@dataclass
class ParseResult:
    tree: Any
    errors: list[str]
    language: SupportedLanguage

class IParser(ABC):
    @abstractmethod
    def parse_file(self, file_path: str, content: str, language: SupportedLanguage) -> ParseResult:
        """Parses the file content into an AST."""
        pass
