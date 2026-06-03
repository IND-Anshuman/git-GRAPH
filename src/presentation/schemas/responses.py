from datetime import datetime
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class RepositorySchema(BaseModel):
    id: str
    name: str
    url: str
    default_branch: str
    status: str
    entity_count: int | None
    file_count: int | None
    created_at: datetime
    updated_at: datetime

class EntitySchema(BaseModel):
    seid: str
    entity_type: str
    name: str
    qualified_name: str
    file_path: str
    language: str
    start_line: int
    end_line: int
    parent_seid: str | None
    metadata: dict

class RelationshipSchema(BaseModel):
    id: str
    relationship_type: str
    source_seid: str
    target_seid: str
    source_name: str | None
    target_name: str | None
    confidence: float
    metadata: dict

class IngestionResultSchema(BaseModel):
    repository_id: str
    status: str
    files_scanned: int
    entities_extracted: int
    relationships_extracted: int
    errors: list[str]

class ErrorSchema(BaseModel):
    detail: str

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    offset: int
    limit: int

class CommitSchema(BaseModel):
    hash: str
    repository_id: str
    author: str
    email: str
    timestamp: datetime
    message: str
    parent_hashes: list[str]
    is_merge: bool
    is_root: bool

class EntityVersionSchema(BaseModel):
    id: str
    seid: str
    commit_hash: str
    version_ordinal: int
    mutation_type: str
    canonical_name: str
    file_path: str
    start_line: int
    end_line: int
    content_hash: str
    structural_fingerprint: str
    source_text: str | None
    metadata: dict

class ChangeEventSchema(BaseModel):
    id: str
    repository_id: str
    commit_hash: str
    seid: str
    change_type: str
    metadata: dict

class TemporalGraphSchema(BaseModel):
    entities: list[EntitySchema]
    relationships: list[RelationshipSchema]

class TimelineSchema(BaseModel):
    commit_hash: str
    timestamp: datetime
    message: str
    changes: list[ChangeEventSchema]

class HealthScoreSchema(BaseModel):
    health_score: float
    reconstruction_score: float
    integrity_score: float
    confidence_score: float
    seid_stability_score: float
    status: str

class IntegrityViolationSchema(BaseModel):
    id: str
    repository_id: str
    violation_type: str
    severity: str
    target_seid: str | None
    description: str
    recommended_repair: str
    is_resolved: bool
    detected_at: datetime

class RepairAuditSchema(BaseModel):
    id: str
    repository_id: str
    operator: str
    issue_ids: list[str]
    repair_actions: list[dict]
    executed_at: datetime

class BenchmarkReportSchema(BaseModel):
    id: str
    repository_id: str
    commit_hash: str
    scan_duration_ms: int
    diff_throughput_nodes_sec: float
    reconstruction_latency_ms: int
    db_size_bytes: int
    memory_rss_bytes: int
    measured_at: datetime
