"""CSS language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class CSSLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for CSS syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.CSS,
            module_name="tree_sitter_css",
            dependency_name="tree-sitter-css",
            entity_queries={
                EntityType.CLASS: "(rule_set selector: (_) @name) @rule",
            },
            relationship_queries={
                "calls": "(declaration name: (property_name) @name) @decl",
            },
        )
