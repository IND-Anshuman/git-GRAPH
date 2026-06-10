"""Java language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class JavaLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for Java syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.JAVA,
            module_name="tree_sitter_java",
            dependency_name="tree-sitter-java",
            entity_queries={
                EntityType.CLASS: "(class_declaration name: (identifier) @name) @class",
                EntityType.INTERFACE: "(interface_declaration name: (identifier) @name) @interface",
                EntityType.ENUM: "(enum_declaration name: (identifier) @name) @enum",
                EntityType.METHOD: "(method_declaration name: (identifier) @name) @method",
                EntityType.VARIABLE: "(field_declaration declarator: (variable_declarator name: (identifier) @name)) @field",
            },
            relationship_queries={
                "imports": "(import_declaration) @import",
                "calls": "(method_invocation name: (identifier) @name) @call",
                "extends": "(superclass (type_identifier) @name) @extends",
                "implements": "(super_interfaces (type_list (type_identifier) @name)) @implements",
            },
        )
