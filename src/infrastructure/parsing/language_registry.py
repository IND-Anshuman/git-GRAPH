"""Language adapter registry."""

from dataclasses import dataclass
from typing import Dict, Iterable, Optional

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import (
    ILanguageAdapter,
    TreeSitterPackageAdapter,
)
from src.infrastructure.parsing.languages.go_adapter import GoLanguageAdapter
from src.infrastructure.parsing.languages.java_adapter import JavaLanguageAdapter
from src.infrastructure.parsing.languages.javascript_adapter import (
    JavaScriptLanguageAdapter,
)
from src.infrastructure.parsing.languages.python_adapter import PythonLanguageAdapter
from src.infrastructure.parsing.languages.typescript_adapter import (
    TypeScriptLanguageAdapter,
)
from src.infrastructure.parsing.languages.csharp_adapter import CSharpLanguageAdapter
from src.infrastructure.parsing.languages.rust_adapter import RustLanguageAdapter
from src.infrastructure.parsing.languages.kotlin_adapter import KotlinLanguageAdapter
from src.infrastructure.parsing.languages.swift_adapter import SwiftLanguageAdapter
from src.infrastructure.parsing.languages.php_adapter import PHPLanguageAdapter
from src.infrastructure.parsing.languages.scala_adapter import ScalaLanguageAdapter
from src.infrastructure.parsing.languages.ruby_adapter import RubyLanguageAdapter
from src.infrastructure.parsing.languages.elixir_adapter import ElixirLanguageAdapter
from src.infrastructure.parsing.languages.html_adapter import HTMLLanguageAdapter
from src.infrastructure.parsing.languages.css_adapter import CSSLanguageAdapter


@dataclass(frozen=True)
class LanguageCapability:
    """Runtime capability summary for a configured language."""

    language: SupportedLanguage
    parser_available: bool
    entity_extraction_supported: bool
    relationship_extraction_supported: bool
    missing_dependency: str | None = None


class LanguageRegistry:
    """Registry for tree-sitter language adapters."""

    def __init__(self):
        self._adapters: Dict[SupportedLanguage, ILanguageAdapter] = {}
        self._register_default_adapters()

    def _register_default_adapters(self) -> None:
        self.register(SupportedLanguage.PYTHON, PythonLanguageAdapter())
        self.register(SupportedLanguage.JAVASCRIPT, JavaScriptLanguageAdapter())
        self.register(SupportedLanguage.TYPESCRIPT, TypeScriptLanguageAdapter())
        self.register(SupportedLanguage.GO, GoLanguageAdapter())
        self.register(SupportedLanguage.JAVA, JavaLanguageAdapter())
        self.register(SupportedLanguage.CSHARP, CSharpLanguageAdapter())
        self.register(SupportedLanguage.RUST, RustLanguageAdapter())
        self.register(SupportedLanguage.KOTLIN, KotlinLanguageAdapter())
        self.register(SupportedLanguage.SWIFT, SwiftLanguageAdapter())
        self.register(SupportedLanguage.PHP, PHPLanguageAdapter())
        self.register(SupportedLanguage.SCALA, ScalaLanguageAdapter())
        self.register(SupportedLanguage.RUBY, RubyLanguageAdapter())
        self.register(SupportedLanguage.ELIXIR, ElixirLanguageAdapter())
        self.register(SupportedLanguage.HTML, HTMLLanguageAdapter())
        self.register(SupportedLanguage.CSS, CSSLanguageAdapter())

    def register(self, language: SupportedLanguage, adapter: ILanguageAdapter) -> None:
        """Register a new language adapter."""
        self._adapters[language] = adapter

    def get_adapter(self, language: SupportedLanguage) -> Optional[ILanguageAdapter]:
        """Get an adapter for a language if its grammar is available."""
        adapter = self._adapters.get(language)
        if adapter and adapter.is_available():
            return adapter
        return None

    def get_declared_adapter(self, language: SupportedLanguage) -> Optional[ILanguageAdapter]:
        """Get a declared adapter even if the underlying grammar is unavailable."""
        return self._adapters.get(language)

    def has_adapter(self, language: SupportedLanguage) -> bool:
        """Check if a language has an available adapter."""
        return self.get_adapter(language) is not None

    def get_capability(self, language: SupportedLanguage) -> LanguageCapability:
        """Return parser/extraction capabilities for one language."""
        adapter = self._adapters.get(language)
        if not adapter:
            return LanguageCapability(
                language=language,
                parser_available=False,
                entity_extraction_supported=False,
                relationship_extraction_supported=False,
                missing_dependency="unregistered",
            )

        parser_available = adapter.is_available()
        return LanguageCapability(
            language=language,
            parser_available=parser_available,
            entity_extraction_supported=parser_available
            and adapter.supports_entity_extraction(),
            relationship_extraction_supported=parser_available
            and adapter.supports_relationship_extraction(),
            missing_dependency=adapter.get_missing_dependency(),
        )

    def list_capabilities(self) -> Iterable[LanguageCapability]:
        """Return parser/extraction capabilities for all registered languages."""
        for language in SupportedLanguage:
            if language == SupportedLanguage.UNKNOWN:
                continue
            yield self.get_capability(language)
