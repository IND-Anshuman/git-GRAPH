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
