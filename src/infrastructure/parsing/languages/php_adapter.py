"""PHP language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class PHPLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for PHP syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.PHP,
            module_name="tree_sitter_php",
            language_function_names=("language_php", "language"),
            dependency_name="tree-sitter-php",
            entity_queries={
                EntityType.CLASS: "(class_declaration name: (name) @name) @class",
                EntityType.INTERFACE: "(interface_declaration name: (name) @name) @interface",
                EntityType.FUNCTION: "(function_definition name: (name) @name) @function",
                EntityType.METHOD: "(method_declaration name: (name) @name) @method",
            },
            relationship_queries={
                "imports": "(namespace_use_clause) @import",
                "calls": "(function_call_expression) @call",
            },
        )
