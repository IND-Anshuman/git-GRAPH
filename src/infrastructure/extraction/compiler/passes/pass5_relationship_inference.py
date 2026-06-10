from src.domain.entities.semantic_compiler_context import SemanticCompilerContext
from src.domain.value_objects.relationship_confidence import RelationshipConfidence
from src.infrastructure.extraction.registries.framework_pack_registry import FrameworkPackRegistry
from src.infrastructure.extraction.compiler.passes.base import ICompilerPass

class Pass5RelationshipInference(ICompilerPass):
    """Pass 5: Relationship Inference. Compiles RelationshipConfidence for each relationship."""
    
    def __init__(self, registry: FrameworkPackRegistry | None = None):
        self.registry = registry or FrameworkPackRegistry()

    def execute(self, context: SemanticCompilerContext) -> None:
        packs = {f: self.registry.get_pack(f) for f in context.frameworks_detected}
        
        for rel in context.raw_relationships:
            # 1. Structural score: based on AST type
            rel_type_name = getattr(rel.relationship_type, "name", str(rel.relationship_type))
            if rel_type_name in ("EXTENDS", "IMPLEMENTS", "BELONGS_TO"):
                structural = 1.0
            elif rel_type_name == "IMPORTS":
                structural = 0.9
            else:
                # Function call
                structural = 0.7
                
            # 2. Framework score: check if framework registry has explicitly mapped this name/relationship
            framework = 0.0
            for pack_name, pack in packs.items():
                pack_rels = pack.get("relationships", {})
                # If target is a special framework component or the relationship name matches framework keys
                if rel.target_name in pack.get("entities", {}):
                    framework = 0.8
                for key, val in pack_rels.items():
                    if key in rel.metadata.get("call_symbol", "") or key == rel_type_name.lower():
                        framework = 1.0
                        break
                        
            # 3. Naming score: Conventions check
            naming = 0.5
            source_lower = rel.source_name.lower()
            target_lower = rel.target_name.lower()
            if "coordinator" in source_lower and "service" in target_lower:
                naming = 0.9
            elif "agent" in source_lower and "tool" in target_lower:
                naming = 1.0
            elif "controller" in source_lower and "service" in target_lower:
                naming = 0.9
            elif "service" in source_lower and "repository" in target_lower:
                naming = 0.9

            # 4. Flow score: Check if there is parameter data flow (e.g. if matched in source text or calls)
            flow = 0.5
            # If the relationship metadata indicates a call with args
            if rel.metadata.get("has_arguments"):
                flow = 0.8

            # Calculate weighted average
            final = 0.35 * structural + 0.30 * framework + 0.20 * naming + 0.15 * flow
            final = min(1.0, max(0.0, final))

            key = (rel.source_name, rel.target_name, rel_type_name)
            context.relationships_confidence[key] = RelationshipConfidence(
                structural_score=structural,
                framework_score=framework,
                naming_score=naming,
                flow_score=flow,
                final_score=final
            )
