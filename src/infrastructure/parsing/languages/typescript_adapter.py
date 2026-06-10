"""TypeScript language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class TypeScriptLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for TypeScript syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.TYPESCRIPT,
            module_name="tree_sitter_typescript",
            language_function_names=("language_typescript", "language"),
            dependency_name="tree-sitter-typescript",
            entity_queries={
                EntityType.CLASS: "(class_declaration name: (type_identifier) @name) @class",
                EntityType.INTERFACE: "(interface_declaration name: (type_identifier) @name) @interface",
                EntityType.FUNCTION: "(function_declaration name: (identifier) @name) @function",
                EntityType.METHOD: "(method_definition name: (_) @name) @method",
                EntityType.TYPE_ALIAS: "(type_alias_declaration name: (type_identifier) @name) @type_alias",
                EntityType.VARIABLE: "(variable_declarator name: (identifier) @name) @variable",
            },
            relationship_queries={
                "imports": "(import_statement) @import",
                "calls": "(call_expression function: (_) @name) @call",
                "extends": "(extends_clause (type_identifier) @name) @extends",
                "implements": "(implements_clause (type_identifier) @name) @implements",
            },
        )
