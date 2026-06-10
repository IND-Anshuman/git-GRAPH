"""Swift language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class SwiftLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for Swift syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.SWIFT,
            module_name="tree_sitter_swift",
            dependency_name="tree-sitter-swift",
            entity_queries={
                EntityType.CLASS: "(class_declaration name: (type_identifier) @name) @class",
                EntityType.INTERFACE: "(protocol_declaration name: (type_identifier) @name) @protocol",
                EntityType.FUNCTION: "(function_declaration name: (simple_identifier) @name) @function",
            },
            relationship_queries={
                "imports": "(import_declaration) @import",
                "calls": "(call_expression) @call",
            },
        )
