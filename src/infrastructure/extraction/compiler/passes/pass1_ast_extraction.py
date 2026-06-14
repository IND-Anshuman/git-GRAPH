from src.infrastructure.extraction.compiler.compiler_context import CompilerContext
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.strategy_registry import ExtractionStrategyRegistry
from src.infrastructure.extraction.compiler.passes.base import ICompilerPass

class Pass1ASTExtraction(ICompilerPass):
    """Pass 1: AST Extraction. Emits Alias, Import, Type, and Provider signals and updates the global semantic graph."""
    
    def __init__(self, language_registry: LanguageRegistry | None = None, strategy_registry: ExtractionStrategyRegistry | None = None):
        self.language_registry = language_registry or LanguageRegistry()
        self.strategy_registry = strategy_registry or ExtractionStrategyRegistry()

    def execute(self, context: CompilerContext) -> None:
        if not context.extraction_result:
            return
            
        context.raw_entities = context.extraction_result.entities
        context.raw_relationships = context.extraction_result.relationships
        
        # Parse AST tree to extract signals
        try:
            lang_str = context.language.upper() if isinstance(context.language, str) else context.language.name
            from src.domain.enums.language import SupportedLanguage
            lang_enum = SupportedLanguage[lang_str]
        except Exception:
            from src.domain.enums.language import SupportedLanguage
            lang_enum = SupportedLanguage.UNKNOWN

        adapter = self.language_registry.get_adapter(lang_enum)
        tree = None
        if adapter:
            parser = adapter.get_parser()
            tree = parser.parse(bytes(context.source_code, "utf8"))

        global_graph = context.project_metadata.get("global_semantic_graph")
        symbol_engine = context.project_metadata.get("symbol_resolution_engine")
        alias_engine = context.project_metadata.get("alias_propagation_engine")
        dependency_resolver = context.project_metadata.get("external_dependency_resolver")

        # Index file if resolution engine components are available
        if global_graph and tree:
            if symbol_engine:
                symbol_engine.index_file(context.file_path, context.source_code, tree, context.language)
            if alias_engine:
                alias_engine.trace_variable_flows(context.file_path, context.source_code, tree)
            if dependency_resolver:
                dependency_resolver.resolve_external_imports(context.file_path, global_graph.imports.get(context.file_path, []))

            # Emit signals onto the context
            context.project_metadata["alias_signals"] = global_graph.aliases.get(context.file_path, {})
            context.project_metadata["import_signals"] = global_graph.imports.get(context.file_path, [])
            context.project_metadata["type_signals"] = global_graph.type_bindings.get(context.file_path, {})
            context.project_metadata["provider_signals"] = list(global_graph.external_dependencies.values())
        
        # Populate context imports based on raw relationships of type IMPORTS
        for rel in context.extraction_result.relationships:
            rel_type = rel.relationship_type
            rel_name = rel_type.name if hasattr(rel_type, "name") else str(rel_type)
            if rel_name == "IMPORTS":
                context.imports.append(rel.target_name)
