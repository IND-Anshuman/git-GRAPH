"""Go language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class GoLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for Go syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.GO,
            module_name="tree_sitter_go",
            dependency_name="tree-sitter-go",
            entity_queries={
                EntityType.FUNCTION: "(function_declaration name: (identifier) @name) @function",
                EntityType.METHOD: "(method_declaration name: (field_identifier) @name) @method",
                EntityType.INTERFACE: "(type_spec name: (type_identifier) @name type: (interface_type)) @interface",
                EntityType.CLASS: "(type_spec name: (type_identifier) @name type: (struct_type)) @struct",
                EntityType.VARIABLE: "(var_spec name: (identifier) @name) @variable",
                EntityType.CONSTANT: "(const_spec name: (identifier) @name) @constant",
            },
            relationship_queries={
                "imports": "(import_spec) @import",
                "calls": "(call_expression function: (_) @name) @call",
            },
        )
