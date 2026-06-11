from typing import Any, List, Optional
from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import IBaseExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR
from src.infrastructure.extraction.semantic_evidence_engine.symbol_graph import SymbolNode, SymbolReference
from src.infrastructure.extraction.semantic_evidence_engine.type_evidence import TypeEvidence
from src.infrastructure.extraction.semantic_evidence_engine.call_site import CallSite
from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan
from src.domain.value_objects.knowledge_confidence import KnowledgeConfidence

class SymbolResolutionExtractor(IBaseExtractor):
    """Pass 1 Symbol Resolution Extractor. Builds the SymbolGraph, TypeEvidence, and CallSite records."""

    def extract(self, tree: Any, source_code: str, file_path: str, ir: EvidenceIR) -> None:
        if tree is None or getattr(tree, "root_node", None) is None:
            return
            
        source_bytes = source_code.encode("utf8")
        
        def text(node: Any) -> str:
            return source_bytes[node.start_byte:node.end_byte].decode("utf8")
            
        def make_span(node: Any) -> SourceSpan:
            return SourceSpan(
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                start_column=node.start_point[1] + 1,
                end_line=node.end_point[0] + 1,
                end_column=node.end_point[1] + 1,
                start_byte=node.start_byte,
                end_byte=node.end_byte
            )

        # 1. Register entities as SymbolNodes
        symbol_nodes_map = {}
        for entity in ir.entities:
            sym_id = f"sym_{entity.name}"
            node = SymbolNode(
                symbol_id=sym_id,
                canonical_name=entity.name,
                aliases=[entity.name],
                scope_id=entity.parent_name or "global"
            )
            ir.symbol_graph.nodes.append(node)
            symbol_nodes_map[entity.name] = sym_id

        # 2. Walk tree to resolve calls, assignments, and scopes
        def walk(node: Any, current_scope: Optional[str] = None) -> None:
            scope = current_scope
            node_type = node.type
            
            if node_type in {"class_declaration", "class_definition", "function_declaration", "function_definition", "method_definition", "method_declaration"}:
                name_node = node.child_by_field_name("name")
                if name_node:
                    scope = text(name_node)
                    
            # Check Assignments for Type Evidence
            if node_type == "assignment":
                left = node.child_by_field_name("left")
                right = node.child_by_field_name("right")
                if left and right:
                    left_text = text(left)
                    right_text = text(right)
                    sym_id = f"sym_{left_text.split('.')[-1]}"
                    
                    if "(" in right_text:
                        inferred = right_text.split("(")[0].strip()
                        if inferred.replace(".", "").isalnum():
                            if left_text not in symbol_nodes_map:
                                symbol_nodes_map[left_text] = sym_id
                                ir.symbol_graph.nodes.append(SymbolNode(
                                    symbol_id=sym_id,
                                    canonical_name=left_text,
                                    aliases=[left_text],
                                    scope_id=scope or "global"
                                ))
                            ir.type_evidence.append(TypeEvidence(
                                symbol_id=sym_id,
                                inferred_type=inferred,
                                source="assignment",
                                confidence=KnowledgeConfidence(0.85, "HEURISTIC", ["constructor_inference"])
                            ))

            # Check Calls for CallSite & SymbolReferences
            elif node_type in {"call", "call_expression", "method_invocation"} and scope:
                func_node = node.child_by_field_name("function")
                if func_node:
                    callee = text(func_node)
                    callee_name = callee.split(".")[-1] if "." in callee else callee
                    
                    args_node = node.child_by_field_name("arguments")
                    arg_count = len(args_node.children) if args_node else 0
                    
                    is_async = (node.parent and node.parent.type == "await_expression")
                    
                    caller_id = symbol_nodes_map.get(scope, f"sym_{scope}")
                    callee_id = symbol_nodes_map.get(callee_name, f"sym_{callee_name}")
                    
                    # Add CallSite
                    ir.call_sites.append(CallSite(
                        caller_entity_id=caller_id,
                        callee_symbol=callee_name,
                        argument_count=arg_count,
                        is_async=is_async,
                        span=make_span(node)
                    ))
                    
                    # Add SymbolReference link
                    ir.symbol_graph.references.append(SymbolReference(
                        source_symbol=caller_id,
                        target_symbol=callee_id,
                        reference_type="CALLS"
                    ))

            for child in node.children:
                walk(child, scope)

        walk(tree.root_node)
