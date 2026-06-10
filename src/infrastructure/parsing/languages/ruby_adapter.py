"""Ruby language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class RubyLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for Ruby syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.RUBY,
            module_name="tree_sitter_ruby",
            dependency_name="tree-sitter-ruby",
            entity_queries={
                EntityType.CLASS: "(class name: [ (constant) (scope_resolution) ] @name) @class",
                EntityType.MODULE: "(module name: [ (constant) (scope_resolution) ] @name) @module",
                EntityType.METHOD: "(method name: (identifier) @name) @method",
            },
            relationship_queries={
                "imports": "(call method: (identifier) @import_call) @import",
                "calls": "(call) @call",
            },
        )
