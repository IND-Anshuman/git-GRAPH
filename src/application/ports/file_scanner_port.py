from abc import ABC, abstractmethod
from dataclasses import dataclass
from src.domain.enums import SupportedLanguage

@dataclass
class ScannedFile:
    path: str
    absolute_path: str
    language: SupportedLanguage
    size_bytes: int

class IFileScanner(ABC):
    @abstractmethod
    def scan_repository(self, repo_path: str) -> list[ScannedFile]:
        """Scans a repository for supported files."""
        pass
