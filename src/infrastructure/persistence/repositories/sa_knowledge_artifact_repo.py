"""SQLAlchemy implementation of IKnowledgeArtifactRepository."""

from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_

from src.domain.entities.knowledge_artifact import KnowledgeArtifact
from src.domain.repositories.knowledge_artifact_repo import IKnowledgeArtifactRepository
from src.infrastructure.persistence.models.knowledge_artifact_model import KnowledgeArtifactModel
from src.infrastructure.persistence.mappers.artifact_mapper import ArtifactMapper

class SAKnowledgeArtifactRepository(IKnowledgeArtifactRepository):
    """SQLAlchemy repository for KnowledgeArtifact entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, artifact: KnowledgeArtifact) -> None:
        """Persist a single knowledge artifact."""
        model = ArtifactMapper.to_model(artifact)
        self.session.merge(model)

    def save_batch(self, artifacts: List[KnowledgeArtifact]) -> None:
        """Persist multiple knowledge artifacts in a single batch."""
        for artifact in artifacts:
            self.save(artifact)

    def get_by_id(self, id: uuid.UUID) -> Optional[KnowledgeArtifact]:
        """Fetch a knowledge artifact by its ID."""
        stmt = select(KnowledgeArtifactModel).where(KnowledgeArtifactModel.id == id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if model:
            return ArtifactMapper.to_entity(model)
        return None

    def list_by_repository(self, repository_id: uuid.UUID) -> List[KnowledgeArtifact]:
        """List all artifacts associated with a repository."""
        stmt = select(KnowledgeArtifactModel).where(KnowledgeArtifactModel.repository_id == repository_id)
        models = self.session.execute(stmt).scalars().all()
        return [ArtifactMapper.to_entity(m) for m in models]

    def list_by_commit(self, repository_id: uuid.UUID, commit_hash: str) -> List[KnowledgeArtifact]:
        """List all artifacts created/observed at a specific commit."""
        stmt = (
            select(KnowledgeArtifactModel)
            .where(
                KnowledgeArtifactModel.repository_id == repository_id,
                KnowledgeArtifactModel.valid_from_commit == commit_hash
            )
        )
        models = self.session.execute(stmt).scalars().all()
        return [ArtifactMapper.to_entity(m) for m in models]

    def get_active_artifacts_at_commit(self, repository_id: uuid.UUID, commit_hashes: List[str]) -> List[KnowledgeArtifact]:
        """Fetch all artifacts that are active (valid) for any commit in the list of ancestors."""
        if not commit_hashes:
            return []
        
        # An artifact is active at a commit if the commit is in the valid range:
        # valid_from_commit is in commit_hashes, and valid_to_commit is either NULL or not in commit_hashes.
        # Let's query matching repository_id
        stmt = (
            select(KnowledgeArtifactModel)
            .where(
                KnowledgeArtifactModel.repository_id == repository_id,
                KnowledgeArtifactModel.valid_from_commit.in_(commit_hashes),
                or_(
                    KnowledgeArtifactModel.valid_to_commit == None,
                    ~KnowledgeArtifactModel.valid_to_commit.in_(commit_hashes)
                )
            )
        )
        models = self.session.execute(stmt).scalars().all()
        return [ArtifactMapper.to_entity(m) for m in models]
