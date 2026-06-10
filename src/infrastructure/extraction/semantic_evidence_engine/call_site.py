from dataclasses import dataclass
from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan

@dataclass(frozen=True)
class CallSite:
    caller_entity_id: str
    callee_symbol: str
    argument_count: int
    is_async: bool
    span: SourceSpan
