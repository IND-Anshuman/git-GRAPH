from typing import Any, Optional
from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import IBaseExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR
from src.infrastructure.extraction.semantic_evidence_engine.raw_signal import RawSignal
from src.infrastructure.extraction.semantic_evidence_engine.domain_evidence import DatabaseEvidence
from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan
from src.domain.value_objects.knowledge_confidence import KnowledgeConfidence

class DataFlowExtractor(IBaseExtractor):
    """Pass 1 Data Flow Extractor. Maps data operations, DB queries, serialization, and returns."""

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

        def walk(node: Any, current_scope: Optional[str] = None) -> None:
            scope = current_scope
            node_type = node.type
            
            if node_type in {"class_declaration", "class_definition", "function_declaration", "function_definition", "method_definition", "method_declaration"}:
                name_node = node.child_by_field_name("name")
                if name_node:
                    scope = text(name_node)
                    
            # 1. Parameter and Return flows
            if node_type == "parameters" and scope:
                for param in node.children:
                    if param.type in {"identifier", "typed_parameter"}:
                        ir.signals.append(RawSignal(
                            id=f"df_param_{param.start_byte}",
                            signal_type="PARAMETER_FLOW",
                            value=text(param),
                            confidence=KnowledgeConfidence(1.0, "AST_MATCH", ["parameter_declaration"]),
                            source_entity_id=scope,
                            span=make_span(param)
                        ))
            elif node_type == "return_statement" and scope:
                ir.signals.append(RawSignal(
                    id=f"df_ret_{node.start_byte}",
                    signal_type="RETURN_FLOW",
                    value=text(node),
                    confidence=KnowledgeConfidence(1.0, "AST_MATCH", ["return_statement"]),
                    source_entity_id=scope,
                    span=make_span(node)
                ))

            # 2. Database, Cache, Serialization calls
            elif node_type in {"call", "call_expression", "method_invocation"} and scope:
                func_node = node.child_by_field_name("function")
                if func_node:
                    func_text = text(func_node)
                    func_lower = func_text.lower()
                    
                    # DB Queries
                    db_op = None
                    for op in ("select", "insert", "update", "delete", "query", "execute"):
                        if op in func_lower:
                            db_op = op.upper()
                            break
                            
                    if db_op or "session" in func_lower or "db" in func_lower:
                        ir.database_evidence.append(DatabaseEvidence(
                            table_name="unknown",
                            operation=db_op or "QUERY",
                            orm="SQLAlchemy" if "session" in func_lower else None,
                            query_type="orm" if "session" in func_lower else "raw",
                            span=make_span(node)
                        ))
                        ir.signals.append(RawSignal(
                            id=f"df_db_{node.start_byte}",
                            signal_type="DATABASE_QUERY",
                            value=func_text,
                            confidence=KnowledgeConfidence(0.85, "HEURISTIC", ["db_function_call"]),
                            source_entity_id=scope,
                            span=make_span(node)
                        ))
                        
                    # Cache Lookups / Invalidations
                    cache_sig = None
                    if "cache.get" in func_lower or "redis.get" in func_lower:
                        cache_sig = "CACHE_LOOKUP"
                    elif any(x in func_lower for x in ("cache.delete", "redis.delete", "cache.invalidate", "redis.expire")):
                        cache_sig = "CACHE_INVALIDATION"
                        
                    if cache_sig:
                        ir.signals.append(RawSignal(
                            id=f"df_cache_{node.start_byte}",
                            signal_type=cache_sig,
                            value=func_text,
                            confidence=KnowledgeConfidence(0.95, "FRAMEWORK_MATCH", [cache_sig.lower()]),
                            source_entity_id=scope,
                            span=make_span(node)
                        ))

                    # Serialization / Deserialization
                    ser_sig = None
                    if any(x in func_lower for x in ("json.dumps", "serialize", "marshal")):
                        ser_sig = "SERIALIZATION"
                    elif any(x in func_lower for x in ("json.loads", "deserialize", "unmarshal")):
                        ser_sig = "DESERIALIZATION"
                        
                    if ser_sig:
                        ir.signals.append(RawSignal(
                            id=f"df_ser_{node.start_byte}",
                            signal_type=ser_sig,
                            value=func_text,
                            confidence=KnowledgeConfidence(0.95, "FRAMEWORK_MATCH", [ser_sig.lower()]),
                            source_entity_id=scope,
                            span=make_span(node)
                        ))

            for child in node.children:
                walk(child, scope)

        walk(tree.root_node)
