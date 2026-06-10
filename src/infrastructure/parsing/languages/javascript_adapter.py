"""JavaScript language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class JavaScriptLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for JavaScript syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.JAVASCRIPT,
            module_name="tree_sitter_javascript",
            dependency_name="tree-sitter-javascript",
            entity_queries={
                EntityType.CLASS: "(class_declaration name: (identifier) @name) @class",
                EntityType.FUNCTION: "(function_declaration name: (identifier) @name) @function",
                EntityType.METHOD: "(method_definition name: (_) @name) @method",
                EntityType.VARIABLE: "(variable_declarator name: (identifier) @name) @variable",
            },
            relationship_queries={
                "imports": "(import_statement) @import",
                "calls": "(call_expression function: (_) @name) @call",
                "extends": "(class_heritage (identifier) @name) @extends",
            },
        )
