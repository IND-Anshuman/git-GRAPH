"""HTML language adapter for tree-sitter."""

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.languages.base import TreeSitterPackageAdapter


class HTMLLanguageAdapter(TreeSitterPackageAdapter):
    """Adapter for HTML syntax parsing."""

    def __init__(self) -> None:
        super().__init__(
            language=SupportedLanguage.HTML,
            module_name="tree_sitter_html",
            dependency_name="tree-sitter-html",
            entity_queries={
                EntityType.CLASS: "(element (start_tag (tag_name) @name)) @element",
            },
            relationship_queries={
                "calls": "(attribute (attribute_name) @name) @attribute",
            },
        )
