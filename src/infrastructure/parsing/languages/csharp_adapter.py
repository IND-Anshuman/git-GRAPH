"""C# language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class CSharpLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for C# syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.CSHARP,
            module_name="tree_sitter_c_sharp",
            dependency_name="tree-sitter-c-sharp",
            entity_queries={
                EntityType.CLASS: "(class_declaration name: (identifier) @name) @class",
                EntityType.INTERFACE: "(interface_declaration name: (identifier) @name) @interface",
                EntityType.METHOD: "(method_declaration name: (identifier) @name) @method",
                EntityType.VARIABLE: "(variable_declarator name: (identifier) @name) @variable",
            },
            relationship_queries={
                "imports": "(using_directive name: (_) @name) @import",
                "calls": "(invocation_expression function: (_) @name) @call",
            },
        )
