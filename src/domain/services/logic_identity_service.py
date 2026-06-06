"""Domain service for generating deterministic identities for logic signatures."""

import uuid

from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId


class LogicIdentityService:
    """Generates deterministic identities for logic signatures."""

    NAMESPACE_LOGIC = uuid.UUID("a7b3c291-5f2e-4d8a-b6c4-e1f0a9d2b5c8")  # Fixed namespace

    @classmethod
    def generate_logic_signature_id(
        cls, repository_id: RepositoryId, entity_seid: SEID, language: str, canonical_name: str
    ) -> uuid.UUID:
        """
        Deterministic UUID5 for logic signatures.

        Args:
            repository_id: The RepositoryId of the repository.
            entity_seid: The SEID of the code entity.
            language: The language of the code entity.
            canonical_name: The canonical name of the logic.

        Returns:
            A deterministic UUID5 unique to the repository, entity, language, and name.
        """
        name_string = f"{repository_id.value}:{entity_seid.value}:{language}:{canonical_name}"
        return uuid.uuid5(cls.NAMESPACE_LOGIC, name_string)
