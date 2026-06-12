from src.infrastructure.extraction.compiler.compiler_context import CompilerContext
from src.domain.value_objects.intelligence_hints import CapabilityHint
from src.infrastructure.extraction.registries.capability_registry import CapabilityRegistry
from src.infrastructure.extraction.compiler.passes.base import ICompilerPass

class Pass7CapabilityHinting(ICompilerPass):
    """Pass 7: Capability Hinting. Maps matching semantic hints, roles, and behaviors to capabilities."""
    
    def __init__(self, registry: CapabilityRegistry | None = None):
        self.registry = registry or CapabilityRegistry()

    def execute(self, context: CompilerContext) -> None:
        caps = self.registry.get_capabilities()
        for cap_name, config in caps.items():
            evidence = []
            
            req_hints = config.get("semantic_hints", [])
            for hint in context.semantic_hints:
                if hint.category == cap_name or hint.value in req_hints or hint.category in req_hints:
                    evidence.append(f"Semantic Hint matches: {hint.category}='{hint.value}'")
            
            req_behaviors = config.get("behaviors", [])
            for entity in context.raw_entities:
                for req in req_behaviors:
                    if req in entity.name.lower() or req in entity.source_text.lower():
                        evidence.append(f"Source match behavior keyword: '{req}' in entity '{entity.name}'")
            
            if evidence:
                confidence = min(1.0, 0.5 + 0.1 * len(evidence))
                context.capability_hints.append(
                    CapabilityHint(
                        capability=cap_name,
                        confidence=confidence,
                        evidence=evidence
                    )
                )
