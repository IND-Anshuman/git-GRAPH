from dataclasses import dataclass
from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan

@dataclass(frozen=True)
class PromptEvidence:
    template: str | None
    variables: list[str]
    span: SourceSpan

@dataclass(frozen=True)
class ToolEvidence:
    name: str
    description: str | None
    span: SourceSpan

@dataclass(frozen=True)
class RetrieverEvidence:
    name: str
    span: SourceSpan

@dataclass(frozen=True)
class ModelInvocationEvidence:
    model_name: str | None
    provider: str | None
    span: SourceSpan

@dataclass(frozen=True)
class MemoryAccessEvidence:
    operation: str  # READ, WRITE
    span: SourceSpan
