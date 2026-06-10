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
        lowered = file_path.lower()

        if lowered.endswith('.py'):
            return SupportedLanguage.PYTHON
        elif lowered.endswith('.js') or lowered.endswith('.jsx') or lowered.endswith('.mjs'):
            return SupportedLanguage.JAVASCRIPT
        elif lowered.endswith('.ts') or lowered.endswith('.tsx'):
            return SupportedLanguage.TYPESCRIPT
        elif lowered.endswith('.go'):
            return SupportedLanguage.GO
        elif lowered.endswith('.java'):
            return SupportedLanguage.JAVA
        elif lowered.endswith('.cs'):
            return SupportedLanguage.CSHARP
        elif lowered.endswith('.rs'):
            return SupportedLanguage.RUST
        elif lowered.endswith('.kt'):
            return SupportedLanguage.KOTLIN
        elif lowered.endswith('.swift'):
            return SupportedLanguage.SWIFT
        elif lowered.endswith('.php'):
            return SupportedLanguage.PHP
        elif lowered.endswith('.scala'):
            return SupportedLanguage.SCALA
        elif lowered.endswith('.rb'):
            return SupportedLanguage.RUBY
        elif lowered.endswith('.ex') or lowered.endswith('.exs'):
            return SupportedLanguage.ELIXIR
        elif lowered.endswith('.html') or lowered.endswith('.htm'):
            return SupportedLanguage.HTML
        elif lowered.endswith('.css'):
            return SupportedLanguage.CSS
        else:
            return SupportedLanguage.UNKNOWN
