from src.infrastructure.extraction.compiler.compiler_context import CompilerContext
from src.domain.value_objects.intelligence_hints import SemanticRole
from src.infrastructure.extraction.registries.framework_pack_registry import FrameworkPackRegistry
from src.infrastructure.extraction.compiler.passes.base import ICompilerPass

class Pass3SemanticRoleInference(ICompilerPass):
    """Pass 3: Semantic Role Inference. Multi-signal inference mapping syntactic nodes to semantic roles."""
    
    def __init__(self, registry: FrameworkPackRegistry | None = None):
        self.registry = registry or FrameworkPackRegistry()

    def execute(self, context: CompilerContext) -> None:
        packs = {f: self.registry.get_pack(f) for f in context.frameworks_detected}
        
        for entity in context.raw_entities:
            scores = {}
            
            def add_score(role: str, val: float, ev: str):
                if role not in scores:
                    scores[role] = (0.0, [])
                cur_score, cur_ev = scores[role]
                scores[role] = (cur_score + val, cur_ev + [ev])
                
            # 1. Name Signals
            name_lower = entity.name.lower()
            name_mappings = {
                "service": "Service",
                "repository": "Repository",
                "coordinator": "Coordinator",
                "orchestrator": "Orchestrator",
                "policy": "Policy",
                "workflow": "Workflow",
                "agent": "Agent",
                "tool": "Tool",
                "planner": "Planner",
                "guardrail": "Guardrail",
                "store": "Store",
                "component": "Component",
                "controller": "Controller",
                "manager": "Coordinator",
                "handler": "Service",
                "view": "Component",
                # HTML Pages/UI Blocks
                "searchpage": "SearchPage",
                "dashboard": "Dashboard",
                "adminpanel": "AdminPanel",
                "wizard": "Wizard",
                "checkoutpage": "CheckoutPage",
                # CSS Style Systems
                "designtoken": "DesignToken",
                "theme": "Theme",
                "colorsystem": "ColorSystem",
                "responsivesystem": "ResponsiveSystem"
            }
            for suffix, role in name_mappings.items():
                if name_lower.endswith(suffix):
                    add_score(role, 0.6, f"Name suffix match: '{suffix}'")
                elif suffix in name_lower:
                    add_score(role, 0.3, f"Name contains: '{suffix}'")

            # 2. Framework Signals
            for pack_name, pack in packs.items():
                pack_entities = pack.get("entities", {})
                if entity.name in pack_entities:
                    mapped_role = pack_entities[entity.name]
                    add_score(mapped_role, 0.9, f"Framework '{pack_name}' mapped entity name to '{mapped_role}'")
                
                decorators = entity.metadata.get("decorators", [])
                pack_decorators = pack.get("decorators", {})
                for dec in decorators:
                    if dec in pack_decorators:
                        mapped_role = pack_decorators[dec]
                        add_score(mapped_role, 1.0, f"Framework '{pack_name}' decorator '{dec}' mapped to '{mapped_role}'")

            # 3. Relationship Signals
            for rel in context.raw_relationships:
                if rel.source_name == entity.name and getattr(rel.relationship_type, "name", None) == "EXTENDS":
                    base_class = rel.target_name.lower()
                    if "agent" in base_class:
                        add_score("Agent", 0.7, f"Extends base class containing 'agent': {rel.target_name}")
                    elif "service" in base_class:
                        add_score("Service", 0.7, f"Extends base class containing 'service': {rel.target_name}")
                    elif "repository" in base_class:
                        add_score("Repository", 0.7, f"Extends base class containing 'repository': {rel.target_name}")

            if scores:
                best_role = max(scores.keys(), key=lambda r: scores[r][0])
                total_score, evidence = scores[best_role]
                confidence = min(1.0, total_score)
                context.inferred_roles[entity.name] = SemanticRole(
                    role_name=best_role,
                    confidence=confidence,
                    evidence=evidence
                )
