from typing import Any
from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import IBaseExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR
from src.infrastructure.extraction.semantic_evidence_engine.raw_signal import RawSignal
from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan
from src.domain.value_objects.knowledge_confidence import KnowledgeConfidence

class FrontendSignalExtractor(IBaseExtractor):
    """Pass 1 Frontend Extractor. Detects React components, Zustand stores, state patterns, and design system hooks."""

    def extract(self, tree: Any, source_code: str, file_path: str, ir: EvidenceIR) -> None:
        if tree is None or getattr(tree, "root_node", None) is None:
            return

        for entity in ir.entities:
            name_lower = entity.name.lower()
            
            sig_type = None
            ent_type_name = getattr(entity.entity_type, "name", str(entity.entity_type))
            
            # 1. State Store
            if "store" in name_lower or "createstore" in name_lower or "usestore" in name_lower:
                sig_type = "STATE_STORE"
            # 2. Reducer / Action
            elif "reducer" in name_lower:
                sig_type = "REDUCER"
            elif "action" in name_lower or "dispatch" in name_lower:
                sig_type = "ACTION"
            # 3. Selectors
            elif "selector" in name_lower:
                sig_type = "SELECTOR"
            # 4. API Query / Mutation hooks
            elif (name_lower.startswith("use") and "query" in name_lower) or "queryhook" in name_lower:
                sig_type = "QUERY_HOOK"
            elif (name_lower.startswith("use") and "mutation" in name_lower) or "mutationhook" in name_lower:
                sig_type = "MUTATION_HOOK"
            # 5. Component / Hook declarations
            elif name_lower.startswith("use") and ent_type_name in ("FUNCTION", "METHOD"):
                sig_type = "HOOK_USAGE"
            # 6. Form validation
            elif "validate" in name_lower or "validation" in name_lower:
                sig_type = "FORM_VALIDATION"
            # 7. Lazy loading and boundaries
            elif "lazy" in name_lower:
                sig_type = "LAZY_COMPONENT"
            elif "suspense" in name_lower:
                sig_type = "SUSPENSE_BOUNDARY"
            elif "errorboundary" in name_lower:
                sig_type = "ERROR_BOUNDARY"
            elif (entity.name and entity.name[0].isupper() and ent_type_name == "CLASS") or "component" in name_lower:
                sig_type = "COMPONENT_DECLARATION"

            if sig_type:
                ir.signals.append(RawSignal(
                    id=f"fe_{sig_type.lower()}_{entity.span.start_byte}",
                    signal_type=sig_type,
                    value=entity.name,
                    confidence=KnowledgeConfidence(0.85, "HEURISTIC", ["frontend_naming_convention"]),
                    source_entity_id=entity.name,
                    span=entity.span
                ))
