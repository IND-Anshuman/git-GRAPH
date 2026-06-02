from datetime import datetime
from pydantic import BaseModel

class RepositoryResponse(BaseModel):
    id: str
    name: str
    url: str
    default_branch: str
    status: str
    entity_count: int | None
    file_count: int | None
    created_at: datetime
    updated_at: datetime

class EntityResponse(BaseModel):
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

class RelationshipResponse(BaseModel):
    id: str
    relationship_type: str
    source_seid: str
    target_seid: str
    source_name: str | None
    target_name: str | None
    confidence: float
    metadata: dict

class IngestionResultResponse(BaseModel):
    repository_id: str
    status: str
    files_scanned: int
    entities_extracted: int
    relationships_extracted: int
    errors: list[str]

class CommitResponse(BaseModel):
    hash: str
    repository_id: str
    author: str
    email: str
    timestamp: datetime
    message: str
    parent_hashes: list[str]
    is_merge: bool
    is_root: bool

class EntityVersionResponse(BaseModel):
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

class ChangeEventResponse(BaseModel):
    id: str
    repository_id: str
    commit_hash: str
    seid: str
    change_type: str
    metadata: dict

class TemporalGraphResponse(BaseModel):
    entities: list[EntityResponse]
    relationships: list[RelationshipResponse]

class TimelineResponse(BaseModel):
    commit_hash: str
    timestamp: datetime
    message: str
    changes: list[ChangeEventResponse]
