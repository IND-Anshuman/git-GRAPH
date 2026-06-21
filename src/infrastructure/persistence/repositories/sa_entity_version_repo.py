"""SQLAlchemy implementation of IEntityVersionRepository."""

from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from src.domain.entities.entity_version import EntityVersion
from src.domain.repositories.entity_version_repo import IEntityVersionRepository
from src.domain.value_objects.entity_id import SEID
from src.infrastructure.persistence.models.entity_version_model import EntityVersionModel
from src.infrastructure.persistence.models.commit_model import CommitModel
from src.infrastructure.persistence.mappers.domain_mapper import DomainMapper

class SAEntityVersionRepository(IEntityVersionRepository):
    """SQLAlchemy repository for EntityVersion entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, version: EntityVersion) -> None:
        """Persist a single entity version."""
        model = DomainMapper.to_entity_version_model(version)
        self.session.merge(model)

    def save_batch(self, versions: list[EntityVersion]) -> None:
        """Persist a list of entity versions in batch."""
        models = [DomainMapper.to_entity_version_model(v) for v in versions]
        self.session.add_all(models)

    def get_by_id(self, id: uuid.UUID) -> Optional[EntityVersion]:
        """Fetch a specific entity version record by ID."""
        model = self.session.get(EntityVersionModel, id)
        if model:
            return DomainMapper.to_entity_version_entity(model)
        return None

    def get_by_commit(self, commit_hash: str) -> List[EntityVersion]:
        """Fetch all entity versions introduced/captured in a commit."""
        stmt = select(EntityVersionModel).where(EntityVersionModel.commit_hash == commit_hash)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_entity_version_entity(m) for m in models]

    def get_by_commits(self, commit_hashes: List[str]) -> List[EntityVersion]:
        """Fetch all entity versions introduced/captured in a list of commits in batch."""
        if not commit_hashes:
            return []
        
        chunk_size = 500
        results = []
        for i in range(0, len(commit_hashes), chunk_size):
            chunk = commit_hashes[i:i + chunk_size]
            stmt = select(EntityVersionModel).where(EntityVersionModel.commit_hash.in_(chunk))
            models = self.session.execute(stmt).scalars().all()
            results.extend([DomainMapper.to_entity_version_entity(m) for m in models])
        return results

    def _get_ancestor_hashes(self, commit_hash: str) -> List[str]:
        """Helper to fetch all ancestor commit hashes of a commit in Python."""
        ancestors = {commit_hash}
        queue = [commit_hash]
        while queue:
            current = queue.pop(0)
            stmt = select(CommitModel.parent_hashes).where(CommitModel.hash == current)
            parents = self.session.execute(stmt).scalar_one_or_none()
            if parents:
                for p in parents:
                    if p not in ancestors:
                        ancestors.add(p)
                        queue.append(p)
        return list(ancestors)

    def get_latest_before_or_at(self, seid: SEID, commit_hash: str) -> Optional[EntityVersion]:
        """Find the active version of an entity at or immediately before a given commit."""
        # 1. Fetch all versions of this entity
        stmt = select(EntityVersionModel).where(EntityVersionModel.seid == seid.value)
        models = self.session.execute(stmt).scalars().all()
        if not models:
            return None

        # 2. Get ancestor commit hashes for the target commit
        ancestor_hashes = set(self._get_ancestor_hashes(commit_hash))

        # 3. Find the version with the highest ordinal that belongs to an ancestor commit
        valid_versions = [
            m for m in models if m.commit_hash in ancestor_hashes
        ]
        if not valid_versions:
            return None

        # Sort by version_ordinal descending and return the first one
        valid_versions.sort(key=lambda x: x.version_ordinal, reverse=True)
        return DomainMapper.to_entity_version_entity(valid_versions[0])

    def list_by_seid(self, seid: SEID) -> List[EntityVersion]:
        """Fetch the chronological evolution timeline of an entity by SEID."""
        stmt = (
            select(EntityVersionModel)
            .where(EntityVersionModel.seid == seid.value)
            .order_by(EntityVersionModel.version_ordinal.asc())
        )
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_entity_version_entity(m) for m in models]
