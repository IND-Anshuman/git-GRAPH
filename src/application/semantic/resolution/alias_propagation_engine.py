"""Alias Propagation Engine for building variable lineage graphs."""

from typing import Any, List, Dict
from src.application.semantic.resolution.global_semantic_graph import GlobalSemanticGraph

class AliasPropagationEngine:
    """Traces the flow of values across local assignments and calls within a file."""

    def __init__(self, global_graph: GlobalSemanticGraph):
        self.global_graph = global_graph

    def trace_variable_flows(self, file_path: str, source_code: str, tree: Any) -> List[Dict[str, Any]]:
        """Traces local variable assignments and registers aliases in the global graph."""
        if tree is None or getattr(tree, "root_node", None) is None:
            return []

        source_bytes = source_code.encode("utf8")

        def text(node: Any) -> str:
            return source_bytes[node.start_byte:node.end_byte].decode("utf8")

        flows = []

        def walk(node: Any) -> None:
            node_type = node.type
            # Check assignments: e.g. a = password
            if node_type in ("assignment", "variable_declarator"):
                left = node.child_by_field_name("left") or node.child_by_field_name("name")
                right = node.child_by_field_name("right") or node.child_by_field_name("value")
                if left and right:
                    left_text = text(left)
                    right_text = text(right)
                    
                    # Clean identifiers
                    if left.type == "identifier" and right.type == "identifier":
                        src_var = right_text
                        tgt_var = left_text
                        flows.append({
                            "source": src_var,
                            "target": tgt_var,
                            "flow_type": "variable_assignment"
                        })
                        self.global_graph.add_alias(file_path, tgt_var, src_var)

            # Check calls to find parameter bindings (e.g. hash(b) passes b to hash function)
            elif node_type in ("call", "call_expression", "method_invocation"):
                func_node = node.child_by_field_name("function")
                args_node = node.child_by_field_name("arguments")
                if func_node and args_node:
                    func_name = text(func_node)
                    # Extract args
                    for arg in args_node.children:
                        if arg.type == "identifier":
                            arg_name = text(arg)
                            flows.append({
                                "source": arg_name,
                                "target": func_name,
                                "flow_type": "call_argument"
                            })

            for child in node.children:
                walk(child)

        walk(tree.root_node)
        return flows
