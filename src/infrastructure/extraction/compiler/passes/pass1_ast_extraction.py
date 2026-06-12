from src.infrastructure.extraction.compiler.compiler_context import CompilerContext
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.strategy_registry import ExtractionStrategyRegistry
from src.infrastructure.extraction.compiler.passes.base import ICompilerPass

class Pass1ASTExtraction(ICompilerPass):
    """Pass 1: AST Extraction. Simply reads raw signals from the pre-populated extraction_result."""
    
    def __init__(self, language_registry: LanguageRegistry | None = None, strategy_registry: ExtractionStrategyRegistry | None = None):
        self.language_registry = language_registry or LanguageRegistry()
        self.strategy_registry = strategy_registry or ExtractionStrategyRegistry()

    def execute(self, context: CompilerContext) -> None:
        if not context.extraction_result:
            return
            
        context.raw_entities = context.extraction_result.entities
        context.raw_relationships = context.extraction_result.relationships
        
        # Populate context imports based on raw relationships of type IMPORTS
        for rel in context.extraction_result.relationships:
            rel_type = rel.relationship_type
            rel_name = rel_type.name if hasattr(rel_type, "name") else str(rel_type)
            if rel_name == "IMPORTS":
                context.imports.append(rel.target_name)
