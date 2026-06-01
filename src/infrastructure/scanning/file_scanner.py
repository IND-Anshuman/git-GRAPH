"""File system scanner for repositories."""

import os
from typing import List
from src.application.ports.file_scanner_port import IFileScanner, ScannedFile
from src.domain.entities.source_file import SourceFile
from src.domain.enums.language import SupportedLanguage

class FileSystemScanner(IFileScanner):
    """Scans the local filesystem for source code files."""
    
    IGNORE_DIRS = {'.git', '__pycache__', '.venv', 'node_modules', '.tox', '.mypy_cache'}
    
    def scan_repository(self, repo_path: str) -> List[ScannedFile]:
        """Walks the repository directory to find source files.
        
        Args:
            repo_path: The absolute path to the repository directory.
            
        Returns:
            A list of ScannedFile objects representing discovered source files.
        """
        results: List[ScannedFile] = []
        
        for root, dirs, files in os.walk(repo_path):
            # Mutate dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                
                language = SourceFile.detect_language(file)
                if language != SupportedLanguage.UNKNOWN:
                    try:
                        size_bytes = os.path.getsize(file_path)
                        results.append(ScannedFile(
                            path=rel_path,
                            language=language,
                            size=size_bytes
                        ))
                    except OSError:
                        # Skip files that can't be stat'd (e.g. broken symlinks)
                        continue
                        
        return results
