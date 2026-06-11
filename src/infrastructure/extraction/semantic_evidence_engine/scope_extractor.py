from typing import Any, List, Optional
from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import IBaseExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR
from src.infrastructure.extraction.semantic_evidence_engine.raw_signal import RawSignal
from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan
from src.domain.value_objects.knowledge_confidence import KnowledgeConfidence

class ScopeExtractor(IBaseExtractor):
    """Pass 1 Scope Extractor. Analyzes active context scopes (global, class, function) and emits Scope signals."""

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

        def walk(node: Any, scope_stack: List[str]) -> None:
            node_type = node.type
            new_scope = None
            
            if node_type in {"class_declaration", "class_definition"}:
                name_node = node.child_by_field_name("name")
                if name_node:
                    new_scope = f"class:{text(name_node)}"
            elif node_type in {"function_declaration", "function_definition", "method_definition", "method_declaration"}:
                name_node = node.child_by_field_name("name")
                if name_node:
                    new_scope = f"function:{text(name_node)}"
            elif node_type == "lambda" or node_type == "arrow_function":
                new_scope = "closure"
                
            current_stack = list(scope_stack)
            if new_scope:
                current_stack.append(new_scope)
                
            # Emit Scope Signal
            if new_scope:
                scope_kind = new_scope.split(":")[0] if ":" in new_scope else new_scope
                signal = RawSignal(
                    id=f"scope_{node.start_byte}",
                    signal_type="SCOPE",
                    value=scope_kind,
                    confidence=KnowledgeConfidence(1.0, "AST_MATCH", ["node_type_scope"]),
                    source_entity_id=new_scope.split(":")[1] if ":" in new_scope else None,
                    span=make_span(node),
                    metadata={"scope_stack": current_stack}
                )
                ir.signals.append(signal)

            for child in node.children:
                walk(child, current_stack)

        walk(tree.root_node, ["global"])
