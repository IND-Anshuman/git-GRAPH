"""Elixir language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class ElixirLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for Elixir syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.ELIXIR,
            module_name="tree_sitter_elixir",
            dependency_name="tree-sitter-elixir",
            entity_queries={
                EntityType.CLASS: "(call target: (identifier) @target_name (arguments (alias) @name)) @module",
                EntityType.FUNCTION: "(call target: (identifier) @target_name (arguments (call) @name)) @function",
            },
            relationship_queries={
                "calls": "(call) @call",
            },
        )
