"""Artifact to Model mapper."""

import uuid
from datetime import datetime
from src.domain.entities.knowledge_artifact import KnowledgeArtifact
from src.infrastructure.persistence.models.knowledge_artifact_model import KnowledgeArtifactModel

class ArtifactMapper:
    """Mapper between domain knowledge artifacts and database models."""

    @staticmethod
    def to_model(entity: KnowledgeArtifact) -> KnowledgeArtifactModel:
        return KnowledgeArtifactModel(
            id=entity.id,
            repository_id=entity.repository_id,
            artifact_type=entity.artifact_type,
            source=entity.source,
            confidence=entity.confidence,
            valid_from_commit=entity.valid_from_commit,
            valid_to_commit=entity.valid_to_commit,
            observed_at=entity.observed_at,
            artifact_version=entity.artifact_version,
            provenance=entity.provenance
        )

    @staticmethod
    def to_entity(model: KnowledgeArtifactModel) -> KnowledgeArtifact:
        return KnowledgeArtifact(
            id=model.id,
            repository_id=model.repository_id,
            artifact_type=model.artifact_type,
            source=model.source,
            confidence=model.confidence,
            valid_from_commit=model.valid_from_commit,
            valid_to_commit=model.valid_to_commit,
            observed_at=model.observed_at,
            artifact_version=model.artifact_version,
            provenance=model.provenance
        )
