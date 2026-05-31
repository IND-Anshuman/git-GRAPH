"""Base class for language-specific parsers."""

from abc import ABC, abstractmethod
from typing import Dict
from tree_sitter import Parser
from src.domain.enums.language import SupportedLanguage
from src.domain.enums.entity_type import EntityType

class ILanguageAdapter(ABC):
    """Adapter interface for tree-sitter language support."""
    
    @abstractmethod
    def get_language(self) -> SupportedLanguage:
        """Get the supported language enum value."""
        pass
        
    @abstractmethod
    def get_parser(self) -> Parser:
        """Get the configured tree-sitter parser."""
        pass
        
    @abstractmethod
    def get_entity_queries(self) -> Dict[EntityType, str]:
        """Get tree-sitter query strings for identifying entities."""
        pass
        
    @abstractmethod
    def get_relationship_queries(self) -> Dict[str, str]:
        """Get tree-sitter query strings for identifying relationships."""
        pass
