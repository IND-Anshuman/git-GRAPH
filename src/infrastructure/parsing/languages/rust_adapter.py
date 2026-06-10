"""Rust language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class RustLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for Rust syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.RUST,
            module_name="tree_sitter_rust",
            dependency_name="tree-sitter-rust",
            entity_queries={
                EntityType.CLASS: "(struct_item name: (type_identifier) @name) @struct",
                EntityType.INTERFACE: "(trait_item name: (type_identifier) @name) @trait",
                EntityType.FUNCTION: "(function_item name: (identifier) @name) @function",
            },
            relationship_queries={
                "imports": "(use_declaration argument: (_) @name) @import",
                "calls": "(call_expression function: (_) @name) @call",
            },
        )
