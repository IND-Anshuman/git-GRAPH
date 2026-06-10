"""Base classes for language-specific parsers."""

from abc import ABC, abstractmethod
from importlib import import_module
from typing import Dict, Iterable

import tree_sitter
from tree_sitter import Parser

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage


class ILanguageAdapter(ABC):
    """Adapter interface for tree-sitter language support."""

    @abstractmethod
    def get_language(self) -> SupportedLanguage:
        """Get the supported language enum value."""

    @abstractmethod
    def get_parser(self) -> Parser:
        """Get the configured tree-sitter parser."""

    @abstractmethod
    def get_entity_queries(self) -> Dict[EntityType, str]:
        """Get tree-sitter query strings for identifying entities."""

    @abstractmethod
    def get_relationship_queries(self) -> Dict[str, str]:
        """Get tree-sitter query strings for identifying relationships."""

    def is_available(self) -> bool:
        """Whether the language grammar is installed and can be loaded."""
        return True

    def get_missing_dependency(self) -> str | None:
        """Describe the missing runtime dependency when unavailable."""
        return None

    def supports_entity_extraction(self) -> bool:
        """Whether the adapter has entity extraction coverage."""
        return bool(self.get_entity_queries())

    def supports_relationship_extraction(self) -> bool:
        """Whether the adapter has relationship extraction coverage."""
        return bool(self.get_relationship_queries())


class TreeSitterPackageAdapter(ILanguageAdapter):
    """Lazy adapter for grammars distributed as Python tree-sitter packages."""

    def __init__(
        self,
        language: SupportedLanguage,
        module_name: str,
        language_function_names: Iterable[str] | None = None,
        entity_queries: Dict[EntityType, str] | None = None,
        relationship_queries: Dict[str, str] | None = None,
        dependency_name: str | None = None,
    ) -> None:
        self._supported_language = language
        self._module_name = module_name
        self._language_function_names = tuple(language_function_names or ("language",))
        self._entity_queries = entity_queries or {}
        self._relationship_queries = relationship_queries or {}
        self._dependency_name = dependency_name or module_name
        self._parser: Parser | None = None
        self._availability_checked = False
        self._is_available = False
        self._missing_dependency: str | None = None

    def get_language(self) -> SupportedLanguage:
        return self._supported_language

    def get_parser(self) -> Parser:
        if self._parser is None:
            language = self._load_language()
            parser = tree_sitter.Parser()
            parser.language = language
            self._parser = parser
        return self._parser

    def get_entity_queries(self) -> Dict[EntityType, str]:
        return self._entity_queries

    def get_relationship_queries(self) -> Dict[str, str]:
        return self._relationship_queries

    def is_available(self) -> bool:
        if not self._availability_checked:
            try:
                self._load_language()
                self._is_available = True
                self._missing_dependency = None
            except Exception:
                self._is_available = False
                self._missing_dependency = self._dependency_name
            self._availability_checked = True
        return self._is_available

    def get_missing_dependency(self) -> str | None:
        if self.is_available():
            return None
        return self._missing_dependency

    def _load_language(self) -> tree_sitter.Language:
        module = import_module(self._module_name)
        for function_name in self._language_function_names:
            language_factory = getattr(module, function_name, None)
            if callable(language_factory):
                return tree_sitter.Language(language_factory())

        raise AttributeError(
            f"No compatible language factory found in module '{self._module_name}'."
        )
