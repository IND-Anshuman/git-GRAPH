from dataclasses import dataclass
from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan

@dataclass(frozen=True)
class ApiEndpointEvidence:
    route: str
    method: str
    entity_id: str
    request_type: str | None
    response_type: str | None
    span: SourceSpan

@dataclass(frozen=True)
class EventEvidence:
    event_name: str
    producer_entity: str
    payload_type: str | None
    span: SourceSpan

@dataclass(frozen=True)
class EventSubscriptionEvidence:
    event_name: str
    consumer_entity: str
    payload_type: str | None
    span: SourceSpan

@dataclass(frozen=True)
class DatabaseEvidence:
    table_name: str
    operation: str  # SELECT, INSERT, UPDATE, DELETE, UPSERT
    orm: str | None
    query_type: str  # raw, orm
    span: SourceSpan
