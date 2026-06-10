from src.domain.entities.semantic_compiler_context import SemanticCompilerContext
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.strategy_registry import ExtractionStrategyRegistry
from src.infrastructure.extraction.compiler.passes.base import ICompilerPass

class Pass1ASTExtraction(ICompilerPass):
    """Pass 1: AST Extraction. Uses language-specific tree-sitter parsers to extract raw signals."""
    
    def __init__(self, language_registry: LanguageRegistry | None = None, strategy_registry: ExtractionStrategyRegistry | None = None):
        self.language_registry = language_registry or LanguageRegistry()
        self.strategy_registry = strategy_registry or ExtractionStrategyRegistry()

    def execute(self, context: SemanticCompilerContext) -> None:
        lang_str = context.language.upper() if isinstance(context.language, str) else context.language.name
        try:
            lang_enum = SupportedLanguage[lang_str]
        except KeyError:
            if isinstance(context.language, SupportedLanguage):
                lang_enum = context.language
            else:
                lang_enum = SupportedLanguage.UNKNOWN
        
        adapter = self.language_registry.get_adapter(lang_enum)
        if not adapter:
            return
            
        parser = adapter.get_parser()
        tree = parser.parse(bytes(context.source_code, "utf8"))
        
        strategy = self.strategy_registry.get(lang_enum)
        if not strategy:
            return
            
        module_name = context.file_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        
        raw_entities = strategy.extract_entities(tree, context.source_code, context.file_path, module_name)
        raw_relationships = strategy.extract_relationships(tree, context.source_code, raw_entities)
        
        context.raw_entities = raw_entities
        context.raw_relationships = raw_relationships
        
        # Populate context imports based on raw relationships of type IMPORTS
        for rel in raw_relationships:
            if getattr(rel.relationship_type, "name", None) == "IMPORTS":
                context.imports.append(rel.target_name)
