"""Tree-sitter parser service."""

from typing import List, Optional
from src.application.ports.parser_port import IParser, ParseResult
from src.domain.enums.language import SupportedLanguage
from src.domain.exceptions import ParsingException
from src.infrastructure.parsing.language_registry import LanguageRegistry

class TreeSitterParserService(IParser):
    """Implementation of IParser using tree-sitter."""
    
    def __init__(self, registry: LanguageRegistry):
        self._registry = registry
        
    def parse_file(self, file_path: str, content: str, language: SupportedLanguage) -> ParseResult:
        """Parses a file's content into an AST.
        
        Args:
            file_path: Path to the file
            content: Source code content
            language: The language of the file
            
        Returns:
            ParseResult containing the tree and any errors
            
        Raises:
            ParsingException: If parsing fails or language is not supported
        """
        adapter = self._registry.get_adapter(language)
        if not adapter:
            raise ParsingException(f"Unsupported language: {language.name} for file {file_path}")
            
        try:
            parser = adapter.get_parser()
            # Convert string content to bytes for tree-sitter
            tree = parser.parse(bytes(content, "utf8"))
            
            # Very basic error detection (tree-sitter sets has_error if parsing fails)
            errors = []
            if tree.root_node.has_error:
                errors.append("AST contains errors")
                
            return ParseResult(tree=tree, errors=errors, language=language)
        except Exception as e:
            raise ParsingException(f"Failed to parse {file_path}: {str(e)}") from e
