from typing import Any, Optional
from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import IBaseExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR
from src.infrastructure.extraction.semantic_evidence_engine.raw_signal import RawSignal
from src.infrastructure.extraction.semantic_evidence_engine.ai_evidence import (
    PromptEvidence, ToolEvidence, RetrieverEvidence, ModelInvocationEvidence, MemoryAccessEvidence
)
from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan
from src.domain.value_objects.knowledge_confidence import KnowledgeConfidence

class AISignalExtractor(IBaseExtractor):
    """Pass 1 AI Extractor. Extracts structured AI agent workflows, tools, templates, and invocations."""

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
            name_lower = entity.name.lower()
            text_lower = entity.source_text.lower()
            
            # 1. Detect AI Agent
            if "agent" in name_lower or "stategraph" in name_lower or "crew" in name_lower:
                ir.signals.append(RawSignal(
                    id=f"ai_agent_{entity.span.start_byte}",
                    signal_type="AGENT_DECLARATION",
                    value=entity.name,
                    confidence=KnowledgeConfidence(0.95, "FRAMEWORK_MATCH", ["agent_name_convention"]),
                    source_entity_id=entity.name,
                    span=entity.span
                ))

            # 2. Detect Tool declarations
            decorators = entity.metadata.get("decorators", [])
            is_tool = False
            for dec in decorators:
                if "@tool" in dec.lower():
                    is_tool = True
                    break
            if "tool" in name_lower:
                is_tool = True
                
            if is_tool:
                ir.ai_evidence.append(ToolEvidence(
                    name=entity.name,
                    description=entity.metadata.get("docstring"),
                    span=entity.span
                ))
                ir.signals.append(RawSignal(
                    id=f"ai_tool_{entity.span.start_byte}",
                    signal_type="TOOL_DECLARATION",
                    value=entity.name,
                    confidence=KnowledgeConfidence(0.95, "FRAMEWORK_MATCH", ["tool_signature"]),
                    source_entity_id=entity.name,
                    span=entity.span
                ))

            # 3. Detect Model Invocations and Providers
            if "openai" in text_lower or "chatgpt" in text_lower or "gemini" in text_lower:
                provider = "openai" if "openai" in text_lower else "google"
                ir.ai_evidence.append(ModelInvocationEvidence(
                    model_name=None,
                    provider=provider,
                    span=entity.span
                ))
                ir.signals.append(RawSignal(
                    id=f"ai_model_{entity.span.start_byte}",
                    signal_type="MODEL_USAGE",
                    value=provider,
                    confidence=KnowledgeConfidence(0.85, "HEURISTIC", ["ai_provider_keyword"]),
                    source_entity_id=entity.name,
                    span=entity.span
                ))

            # 4. Detect Prompts and Templates
            if "prompt" in name_lower or "template" in name_lower:
                ir.ai_evidence.append(PromptEvidence(
                    template=entity.source_text,
                    variables=[],
                    span=entity.span
                ))
                ir.signals.append(RawSignal(
                    id=f"ai_prompt_{entity.span.start_byte}",
                    signal_type="PROMPT_TEMPLATE",
                    value=entity.name,
                    confidence=KnowledgeConfidence(0.85, "HEURISTIC", ["prompt_name_match"]),
                    source_entity_id=entity.name,
                    span=entity.span
                ))

            # 5. Detect Memory accesses
            if "memory" in name_lower or "memory.save" in text_lower or "memory.load" in text_lower:
                op = "WRITE" if "save" in text_lower else "READ"
                ir.ai_evidence.append(MemoryAccessEvidence(
                    operation=op,
                    span=entity.span
                ))
                ir.signals.append(RawSignal(
                    id=f"ai_mem_{entity.span.start_byte}",
                    signal_type="MEMORY_ACCESS",
                    value=op,
                    confidence=KnowledgeConfidence(0.85, "HEURISTIC", ["memory_keyword"]),
                    source_entity_id=entity.name,
                    span=entity.span
                ))
