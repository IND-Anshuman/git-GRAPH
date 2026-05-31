import hashlib
import uuid

from src.domain.enums.entity_type import EntityType
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId

class EntityIdentityService:
    """Service for generating and managing entity identities."""

    NAMESPACE_CODE_KNOWLEDGE_GRAPH = uuid.UUID("f39e3ba0-8a7c-4828-9717-d1a1b15c9ff8")

    @classmethod
    def generate_seid(cls, entity_type: EntityType, qualified_name: str, file_path: str, repo_id: RepositoryId) -> SEID:
        """Generate a deterministic UUID5 SEID from the components."""
        name_string = f"{repo_id.value}:{file_path}:{entity_type.name}:{qualified_name}"
        generated_uuid = uuid.uuid5(cls.NAMESPACE_CODE_KNOWLEDGE_GRAPH, name_string)
        return SEID(value=generated_uuid)

    @staticmethod
    def compute_content_hash(source: str) -> str:
        """Compute a SHA-256 hash of the source text."""
        return hashlib.sha256(source.encode('utf-8')).hexdigest()

    @staticmethod
    def compute_qualified_name(name: str, parent_name: str | None, module_name: str | None) -> str:
        """Compute the fully qualified name for an entity."""
        parts = []
        if module_name:
            parts.append(module_name)
        if parent_name:
            parts.append(parent_name)
        parts.append(name)
        return ".".join(parts)
