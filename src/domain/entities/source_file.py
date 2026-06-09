from dataclasses import dataclass

from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId

@dataclass
class SourceFile:
    """Entity representing a source code file."""
    id: FileId
    repository_id: RepositoryId
    file_path: str
    language: SupportedLanguage
    content_hash: str | None = None
    line_count: int | None = None
    size_bytes: int | None = None

    @staticmethod
    def detect_language(file_path: str) -> SupportedLanguage:
        """Detect the programming language from the file extension."""
        if file_path.endswith('.py'):
            return SupportedLanguage.PYTHON
        elif file_path.endswith('.js') or file_path.endswith('.jsx') or file_path.endswith('.mjs'):
            return SupportedLanguage.JAVASCRIPT
        elif file_path.endswith('.ts') or file_path.endswith('.tsx'):
            return SupportedLanguage.TYPESCRIPT
        elif file_path.endswith('.go'):
            return SupportedLanguage.GO
        elif file_path.endswith('.java'):
            return SupportedLanguage.JAVA
        elif file_path.endswith('.html') or file_path.endswith('.htm'):
            return SupportedLanguage.HTML
        elif file_path.endswith('.css'):
            return SupportedLanguage.CSS
        else:
            return SupportedLanguage.UNKNOWN
