"""Python language adapter for tree-sitter."""

from typing import Dict
import tree_sitter
import tree_sitter_python
from src.domain.enums.language import SupportedLanguage
from src.domain.enums.entity_type import EntityType
from src.infrastructure.parsing.languages.base import ILanguageAdapter

class PythonLanguageAdapter(ILanguageAdapter):
    """Adapter for Python language parsing."""
    
    def __init__(self):
        self._language = tree_sitter.Language(tree_sitter_python.language())
        self._parser = tree_sitter.Parser()
        self._parser.language = self._language
        
    def get_language(self) -> SupportedLanguage:
        return SupportedLanguage.PYTHON
        
    def get_parser(self) -> tree_sitter.Parser:
        return self._parser
        
    def get_entity_queries(self) -> Dict[EntityType, str]:
        return {
            EntityType.CLASS: "(class_definition name: (identifier) @name) @class",
            EntityType.FUNCTION: "(function_definition name: (identifier) @name) @function",
            EntityType.METHOD: "(class_definition body: (block (function_definition name: (identifier) @name) @method))",
            EntityType.VARIABLE: "(assignment left: (identifier) @name) @variable",
            EntityType.DECORATOR: "(decorator) @decorator"
        }
        
    def get_relationship_queries(self) -> Dict[str, str]:
        return {
            "imports": "(import_statement) @import",
            "import_from": "(import_from_statement) @import_from",
            "calls": "(call function: (identifier) @name) @call"
        }
