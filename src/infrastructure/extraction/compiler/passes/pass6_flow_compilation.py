import uuid
from src.domain.entities.semantic_compiler_context import SemanticCompilerContext
from src.application.semantic.isr.canonical_flow import CanonicalFlow
from src.infrastructure.extraction.compiler.passes.base import ICompilerPass

class Pass6FlowCompilation(ICompilerPass):
    """Pass 6: Flow Compilation. Performs DFS multi-hop tracing across relationships to build execution flows."""

    def execute(self, context: SemanticCompilerContext) -> None:
        # Build adjacency list from calls
        adj = {}
        for rel in context.raw_relationships:
            rel_type_name = getattr(rel.relationship_type, "name", str(rel.relationship_type))
            if rel_type_name == "CALLS":
                adj.setdefault(rel.source_name, []).append(rel.target_name)
                
        # Find paths of length >= 2 (multi-hop)
        flows_found = []
        
        def dfs(curr: str, path: list, visited: set):
            if len(path) >= 3:
                # We have source -> intermediate -> target
                flows_found.append(list(path))
                if len(path) >= 4:
                    return # Cap path depth to avoid explosion
            
            for neighbor in adj.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, path, visited)
                    path.pop()
                    visited.remove(neighbor)

        for start in adj:
            dfs(start, [start], {start})
            
        for path in flows_found:
            source = path[0]
            target = path[-1]
            intermediates = path[1:-1]
            
            # Classify flow type
            flow_type = "EXECUTION_FLOW"
            
            # Look up inferred roles to classify flow type
            source_role = context.inferred_roles.get(source)
            target_role = context.inferred_roles.get(target)
            
            has_agent = any(
                context.inferred_roles.get(node).role_name in ("Agent", "Planner", "Tool", "Guardrail")
                for node in path if node in context.inferred_roles
            )
            
            if has_agent:
                flow_type = "AI_AGENT_WORKFLOW"
            elif any("controller" in node.lower() or "api" in node.lower() for node in path):
                flow_type = "REQUEST_RESPONSE_FLOW"
            elif any("consumer" in node.lower() or "producer" in node.lower() or "event" in node.lower() for node in path):
                flow_type = "EVENT_FLOW"
                
            # Compute confidence as average relationship confidence of edges
            conf_sum = 0.0
            edge_count = 0
            for i in range(len(path) - 1):
                key = (path[i], path[i+1], "CALLS")
                conf = context.relationships_confidence.get(key)
                if conf:
                    conf_sum += conf.final_score
                    edge_count += 1
            confidence = (conf_sum / edge_count) if edge_count > 0 else 0.7
            
            flow = CanonicalFlow(
                id=str(uuid.uuid4()),
                flow_type=flow_type,
                source_entity_id=source,
                target_entity_id=target,
                intermediate_entities=intermediates,
                confidence=confidence,
                metadata={"path": path}
            )
            context.flows.append(flow)
