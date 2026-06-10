"""Kotlin language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class KotlinLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for Kotlin syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.KOTLIN,
            module_name="tree_sitter_kotlin",
            dependency_name="tree-sitter-kotlin",
            entity_queries={
                EntityType.CLASS: "(class_declaration name: (type_identifier) @name) @class",
                EntityType.INTERFACE: "(interface_declaration name: (type_identifier) @name) @interface",
                EntityType.FUNCTION: "(function_declaration name: (simple_identifier) @name) @function",
            },
            relationship_queries={
                "imports": "(import_header) @import",
                "calls": "(call_expression) @call",
            },
        )
