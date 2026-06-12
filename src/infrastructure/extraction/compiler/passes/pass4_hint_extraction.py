from src.infrastructure.extraction.compiler.compiler_context import CompilerContext
from src.domain.value_objects.intelligence_hints import SemanticHint
from src.infrastructure.extraction.registries.semantic_hint_registry import SemanticHintRegistry
from src.infrastructure.extraction.compiler.passes.base import ICompilerPass

class Pass4HintExtraction(ICompilerPass):
    """Pass 4: Hint Extraction. Processes fuzzy token/regex-based categorization hints."""
    
    def __init__(self, registry: SemanticHintRegistry | None = None):
        self.registry = registry or SemanticHintRegistry()

    def execute(self, context: CompilerContext) -> None:
        seen_hints = set()
        
        for entity in context.raw_entities:
            # Check name
            categories = self.registry.get_hints_for_token(entity.name)
            for cat in categories:
                key = (entity.name, cat)
                if key not in seen_hints:
                    seen_hints.add(key)
                    context.semantic_hints.append(
                        SemanticHint(
                            category=cat,
                            value=entity.name,
                            confidence=0.8,
                            evidence=[f"Entity name '{entity.name}' matched fuzzy tokens for '{cat}'"]
                        )
                    )
            
            # Check inner calls/identifiers from source code block
            # Scan source code for keywords in registry
            # We can scan lowercase tokens
            for cat, tokens in self.registry._hints.items():
                for t in tokens:
                    if t in entity.source_text.lower():
                        key = (entity.name, cat)
                        if key not in seen_hints:
                            seen_hints.add(key)
                            context.semantic_hints.append(
                                SemanticHint(
                                    category=cat,
                                    value=t,
                                    confidence=0.6,
                                    evidence=[f"Entity source code contains token '{t}' matching '{cat}'"]
                                )
                            )
                            
        # Also check imports
        for imp in context.imports:
            categories = self.registry.get_hints_for_token(imp)
            for cat in categories:
                key = ("<module_import>", cat)
                if key not in seen_hints:
                    seen_hints.add(key)
                    context.semantic_hints.append(
                        SemanticHint(
                            category=cat,
                            value=imp,
                            confidence=0.7,
                            evidence=[f"File imports '{imp}' which matches fuzzy tokens for '{cat}'"]
                        )
                    )
