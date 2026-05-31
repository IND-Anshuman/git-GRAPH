"""Language adapter registry."""

from typing import Dict, Optional
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import ILanguageAdapter
from src.infrastructure.parsing.languages.python_adapter import PythonLanguageAdapter

class LanguageRegistry:
    """Registry for tree-sitter language adapters."""
    
    def __init__(self):
        self._adapters: Dict[SupportedLanguage, ILanguageAdapter] = {}
        # Pre-register Python
        self.register(SupportedLanguage.PYTHON, PythonLanguageAdapter())
        
    def register(self, language: SupportedLanguage, adapter: ILanguageAdapter) -> None:
        """Register a new language adapter."""
        self._adapters[language] = adapter
        
    def get_adapter(self, language: SupportedLanguage) -> Optional[ILanguageAdapter]:
        """Get an adapter for a language if supported."""
        return self._adapters.get(language)
        
    def has_adapter(self, language: SupportedLanguage) -> bool:
        """Check if a language has a registered adapter."""
        return language in self._adapters
