from typing import Any
from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import IBaseExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR
from src.infrastructure.extraction.semantic_evidence_engine.raw_signal import RawSignal
from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan
from src.domain.value_objects.knowledge_confidence import KnowledgeConfidence

class ControlFlowExtractor(IBaseExtractor):
    """Pass 1 Control Flow Extractor. Analyzes syntax branching structures and emits control flow signals."""

    def extract(self, tree: Any, source_code: str, file_path: str, ir: EvidenceIR) -> None:
        if tree is None or getattr(tree, "root_node", None) is None:
            return
            
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

        def walk(node: Any):
            node_type = node.type
            sig_type = None
            
            if node_type in {"if_statement", "conditional_expression"}:
                sig_type = "CONDITIONAL"
            elif node_type in {"for_statement", "while_statement", "for_in_statement"}:
                sig_type = "LOOP"
            elif node_type in {"match_statement", "case_statement", "switch_statement"}:
                sig_type = "MATCH_CASE"
            elif node_type == "try_statement":
                sig_type = "TRY_BLOCK"
            elif node_type in {"except_clause", "catch_clause"}:
                sig_type = "CATCH_BLOCK"
            elif node_type == "finally_clause":
                sig_type = "FINALLY_BLOCK"
                
            if sig_type:
                ir.signals.append(RawSignal(
                    id=f"cf_{node_type}_{node.start_byte}",
                    signal_type=sig_type,
                    value=node_type,
                    confidence=KnowledgeConfidence(1.0, "AST_MATCH", ["control_flow_syntax"]),
                    source_entity_id=None,
                    span=make_span(node)
                ))
                
            for child in node.children:
                walk(child)

        walk(tree.root_node)
