"""SQLAlchemy implementation of ICommitRepository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.domain.entities.commit import Commit
from src.domain.repositories.commit_repo import ICommitRepository
from src.domain.value_objects.repository_id import RepositoryId
from src.infrastructure.persistence.models.commit_model import CommitModel
from src.infrastructure.persistence.mappers.domain_mapper import DomainMapper

class SACommitRepository(ICommitRepository):
    """SQLAlchemy repository for Commit entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, commit: Commit) -> None:
        """Persist a commit entity using merge (insert or update)."""
        model = DomainMapper.to_commit_model(commit)
        self.session.merge(model)

    def get_by_hash(self, commit_hash: str) -> Optional[Commit]:
        """Fetch a commit by its SHA-1 hash."""
        model = self.session.get(CommitModel, commit_hash)
        if model:
            return DomainMapper.to_commit_entity(model)
        return None

    def list_by_repository(self, repository_id: RepositoryId) -> List[Commit]:
        """Fetch all commits for a specific repository, ordered chronologically."""
        stmt = (
            select(CommitModel)
            .where(CommitModel.repository_id == repository_id.value)
            .order_by(CommitModel.timestamp.asc())
        )
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_commit_entity(m) for m in models]
