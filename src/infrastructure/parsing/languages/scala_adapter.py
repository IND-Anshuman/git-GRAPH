"""Scala language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class ScalaLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for Scala syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.SCALA,
            module_name="tree_sitter_scala",
            dependency_name="tree-sitter-scala",
            entity_queries={
                EntityType.CLASS: "(class_definition name: (identifier) @name) @class",
                EntityType.INTERFACE: "(trait_definition name: (identifier) @name) @trait",
                EntityType.METHOD: "(function_definition name: (identifier) @name) @method",
            },
            relationship_queries={
                "imports": "(import_declaration) @import",
                "calls": "(call_expression) @call",
            },
        )
