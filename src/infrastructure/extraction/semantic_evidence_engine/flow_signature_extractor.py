from typing import Any, Optional
from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import IBaseExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR
from src.infrastructure.extraction.semantic_evidence_engine.raw_flow_signature import RawFlowSignature
from src.domain.value_objects.knowledge_confidence import KnowledgeConfidence

class FlowSignatureExtractor(IBaseExtractor):
    """Pass 1 Flow Signature Extractor. Computes execution metrics like loop count and async boundaries."""

    def extract(self, tree: Any, source_code: str, file_path: str, ir: EvidenceIR) -> None:
        if tree is None or getattr(tree, "root_node", None) is None:
            return
            
        def find_node(node: Any, start_byte: int, end_byte: int) -> Optional[Any]:
            if node.start_byte == start_byte and node.end_byte == end_byte:
                return node
            for child in node.children:
                res = find_node(child, start_byte, end_byte)
                if res:
                    return res
            return None

        local_names = {e.name for e in ir.entities}

        for entity in ir.entities:
            if entity.span is None:
                continue
                
            func_node = find_node(tree.root_node, entity.span.start_byte, entity.span.end_byte)
            if not func_node:
                continue
                
            node_count = 0
            branch_count = 0
            loop_count = 0
            async_boundary_count = 0
            external_call_count = 0
            
            def count_flow_metrics(node: Any):
                nonlocal node_count, branch_count, loop_count, async_boundary_count, external_call_count
                
                for child in node.children:
                    nt = child.type
                    if nt in {"call", "call_expression", "method_invocation"}:
                        node_count += 1
                        func_target_node = child.child_by_field_name("function")
                        if func_target_node:
                            target_name = source_code.encode("utf-8")[func_target_node.start_byte:func_target_node.end_byte].decode("utf-8")
                            target_base = target_name.split(".")[-1] if "." in target_name else target_name
                            if target_base not in local_names:
                                external_call_count += 1
                    elif nt in {"if_statement", "elif_clause", "conditional_expression"}:
                        branch_count += 1
                    elif nt in {"for_statement", "while_statement", "for_in_statement"}:
                        loop_count += 1
                    elif nt in {"await_expression", "async_function_definition", "async_method_definition"}:
                        async_boundary_count += 1
                        
                    count_flow_metrics(child)
                    
            count_flow_metrics(func_node)
            
            sig = RawFlowSignature(
                entity_id=entity.name,
                node_count=node_count,
                branch_count=branch_count,
                loop_count=loop_count,
                async_boundary_count=async_boundary_count,
                external_call_count=external_call_count,
                confidence=KnowledgeConfidence(1.0, "AST_MATCH", ["flow_metrics"])
            )
            ir.flow_signatures.append(sig)
