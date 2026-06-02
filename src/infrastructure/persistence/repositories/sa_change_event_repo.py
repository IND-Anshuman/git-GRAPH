"""SQLAlchemy implementation of IChangeEventRepository."""

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.domain.entities.change_event import ChangeEvent
from src.domain.repositories.change_event_repo import IChangeEventRepository
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId
from src.infrastructure.persistence.models.change_event_model import ChangeEventModel
from src.infrastructure.persistence.mappers.domain_mapper import DomainMapper

class SAChangeEventRepository(IChangeEventRepository):
    """SQLAlchemy repository for ChangeEvent entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, event: ChangeEvent) -> None:
        """Persist a single change event."""
        model = DomainMapper.to_change_event_model(event)
        self.session.merge(model)

    def save_batch(self, events: list[ChangeEvent]) -> None:
        """Persist a batch of change events."""
        models = [DomainMapper.to_change_event_model(e) for e in events]
        self.session.add_all(models)

    def get_by_commit(self, commit_hash: str) -> List[ChangeEvent]:
        """Fetch all change events introduced in a commit."""
        stmt = select(ChangeEventModel).where(ChangeEventModel.commit_hash == commit_hash)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_change_event_entity(m) for m in models]

    def list_by_seid(self, seid: SEID) -> List[ChangeEvent]:
        """Fetch all change events that happened to a specific entity."""
        stmt = select(ChangeEventModel).where(ChangeEventModel.seid == seid.value)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_change_event_entity(m) for m in models]

    def list_by_repository(self, repository_id: RepositoryId) -> List[ChangeEvent]:
        """Fetch all change events in a repository (timeline), ordered chronologically by commit."""
        # Note: We can join with CommitModel to sort by commit timestamp
        # But a simple query on change_events is also functional.
        # Let's perform a join with CommitModel for accurate sorting.
        from src.infrastructure.persistence.models.commit_model import CommitModel
        stmt = (
            select(ChangeEventModel)
            .join(CommitModel, ChangeEventModel.commit_hash == CommitModel.hash)
            .where(ChangeEventModel.repository_id == repository_id.value)
            .order_by(CommitModel.timestamp.asc())
        )
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_change_event_entity(m) for m in models]
