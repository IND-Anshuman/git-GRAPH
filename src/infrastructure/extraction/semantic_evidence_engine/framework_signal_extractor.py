from typing import Any, Optional
from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import IBaseExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR
from src.infrastructure.extraction.semantic_evidence_engine.raw_signal import RawSignal
from src.infrastructure.extraction.semantic_evidence_engine.domain_evidence import ApiEndpointEvidence
from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan
from src.domain.value_objects.knowledge_confidence import KnowledgeConfidence

class FrameworkSignalExtractor(IBaseExtractor):
    """Pass 1 Framework Extractor. Extracts routing endpoints, dependency injections, and decorators."""

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

        for entity in ir.entities:
            decorators = entity.metadata.get("decorators", [])
            for dec in decorators:
                dec_lower = dec.lower()
                # 1. API Endpoints
                route = None
                method = "GET"
                
                # Check FastAPI
                if any(x in dec_lower for x in ("@app.get", "@router.get")):
                    route = "/"
                    method = "GET"
                elif any(x in dec_lower for x in ("@app.post", "@router.post")):
                    route = "/"
                    method = "POST"
                elif any(x in dec_lower for x in ("@app.put", "@router.put")):
                    route = "/"
                    method = "PUT"
                elif any(x in dec_lower for x in ("@app.delete", "@router.delete")):
                    route = "/"
                    method = "DELETE"
                # Check Spring Boot annotation
                elif "@getmapping" in dec_lower:
                    route = "/"
                    method = "GET"
                elif "@postmapping" in dec_lower:
                    route = "/"
                    method = "POST"
                    
                if route is not None:
                    if "(" in dec:
                        try:
                            route = dec.split("(")[1].split(")")[0].strip("\"'")
                        except Exception:
                            pass
                            
                    ir.api_evidence.append(ApiEndpointEvidence(
                        route=route,
                        method=method,
                        entity_id=entity.name,
                        request_type=None,
                        response_type=None,
                        span=entity.span
                    ))
                    
                    ir.signals.append(RawSignal(
                        id=f"fw_endpoint_{entity.span.start_byte}",
                        signal_type="RPC_ENDPOINT",
                        value=f"{method} {route}",
                        confidence=KnowledgeConfidence(0.95, "FRAMEWORK_MATCH", ["api_route_decorator"]),
                        source_entity_id=entity.name,
                        span=entity.span
                    ))
                
                # 2. Dependency Injection decorators
                di_sig = None
                if "@autowired" in dec_lower:
                    di_sig = "SERVICE_RESOLUTION"
                elif "@inject" in dec_lower:
                    di_sig = "SERVICE_RESOLUTION"
                elif "depends" in dec_lower:
                    di_sig = "DEPENDENCY_INJECTION"
                    
                if di_sig:
                    ir.signals.append(RawSignal(
                        id=f"fw_di_{entity.span.start_byte}",
                        signal_type=di_sig,
                        value=dec,
                        confidence=KnowledgeConfidence(0.95, "FRAMEWORK_MATCH", [di_sig.lower()]),
                        source_entity_id=entity.name,
                        span=entity.span
                    ))

            # Lifetime checks inside source_text
            text_lower = entity.source_text.lower()
            lifetime = None
            if "addsingleton" in text_lower or "singleton" in text_lower:
                lifetime = "LIFETIME_SINGLETON"
            elif "addscoped" in text_lower or "scoped" in text_lower:
                lifetime = "LIFETIME_SCOPED"
            elif "addtransient" in text_lower or "transient" in text_lower:
                lifetime = "LIFETIME_TRANSIENT"
                
            if lifetime:
                ir.signals.append(RawSignal(
                    id=f"fw_lifetime_{entity.span.start_byte}",
                    signal_type=lifetime,
                    value=lifetime.split("_")[-1],
                    confidence=KnowledgeConfidence(0.85, "HEURISTIC", ["lifetime_text_search"]),
                    source_entity_id=entity.name,
                    span=entity.span
                ))
