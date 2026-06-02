"""SQLAlchemy implementation of IRepositorySnapshotRepository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.domain.entities.repository_snapshot import RepositorySnapshot
from src.domain.repositories.snapshot_repo import IRepositorySnapshotRepository
from src.domain.value_objects.repository_id import RepositoryId
from src.infrastructure.persistence.models.snapshot_model import RepositorySnapshotModel
from src.infrastructure.persistence.mappers.domain_mapper import DomainMapper

class SARepositorySnapshotRepository(IRepositorySnapshotRepository):
    """SQLAlchemy repository for RepositorySnapshot entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, snapshot: RepositorySnapshot) -> None:
        """Persist a repository snapshot checkpoint."""
        model = DomainMapper.to_snapshot_model(snapshot)
        self.session.merge(model)

    def get_by_commit(self, repository_id: RepositoryId, commit_hash: str) -> Optional[RepositorySnapshot]:
        """Fetch snapshot for a specific commit hash, if it exists."""
        stmt = (
            select(RepositorySnapshotModel)
            .where(
                RepositorySnapshotModel.repository_id == repository_id.value,
                RepositorySnapshotModel.commit_hash == commit_hash
            )
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        if model:
            return DomainMapper.to_snapshot_entity(model)
        return None

    def get_latest_before_or_at_commits(self, repository_id: RepositoryId, commit_hashes: list[str]) -> Optional[RepositorySnapshot]:
        """Find the latest snapshot corresponding to any commit in the list (ancestry path)."""
        if not commit_hashes:
            return None

        # Check if there is a snapshot in the ancestry path. We query the snapshot matching the commit hashes.
        # Since we want to find the latest (most recent) one, the input commit_hashes list should be ordered
        # from the latest (target commit) to the oldest (repository root).
        # We can find all snapshots matching these hashes and order them according to their position in commit_hashes.
        stmt = (
            select(RepositorySnapshotModel)
            .where(
                RepositorySnapshotModel.repository_id == repository_id.value,
                RepositorySnapshotModel.commit_hash.in_(commit_hashes)
            )
        )
        models = self.session.execute(stmt).scalars().all()
        if not models:
            return None

        # Map by commit_hash to models
        models_by_hash = {m.commit_hash: m for m in models}

        # Order by the ancestry list order (first match wins, since it's closest to the target)
        for h in commit_hashes:
            if h in models_by_hash:
                return DomainMapper.to_snapshot_entity(models_by_hash[h])

        return None
