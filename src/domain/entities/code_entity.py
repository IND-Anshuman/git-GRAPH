from dataclasses import dataclass, field
from typing import Any

from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.domain.value_objects.fingerprint import StructuralFingerprint

@dataclass
class CodeEntity:
    """Entity representing a discrete code unit."""
    seid: SEID
    entity_type: EntityType
    name: str
    qualified_name: str
    file_id: FileId
    repository_id: RepositoryId
    parent_seid: SEID | None
    language: SupportedLanguage
    location: CodeLocation
    content_hash: str | None = None
    structural_fingerprint: StructuralFingerprint | None = None
    source_text: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
