"""Cross File Call Resolver for resolving function calls across files."""

from typing import Optional
from src.application.semantic.resolution.global_semantic_graph import GlobalSemanticGraph

class CrossFileCallResolver:
    """Resolves local function/method calls to their repository-wide canonical symbols."""

    def __init__(self, global_graph: GlobalSemanticGraph):
        self.global_graph = global_graph

    def resolve_call(self, file_path: str, callee_name: str, scope_id: Optional[str] = None) -> Optional[str]:
        """Resolves a local callee name in a file to its canonical qualified name globally."""
        # Use the global semantic graph's resolution logic
        resolved = self.global_graph.resolve_symbol(file_path, callee_name, scope_id)
        
        # If the resolved name exists in our symbols, return it
        if resolved in self.global_graph.symbols:
            return resolved
            
        # Fallback: check if the target has an alias or matches suffix in symbols
        for qname in self.global_graph.symbols:
            if qname.endswith(resolved):
                return qname
                
        return resolved
