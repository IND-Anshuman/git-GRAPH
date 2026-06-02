"""Use case for fetching the chronological timeline of repository mutations."""

from typing import Callable, List
import uuid

from src.application.ports.unit_of_work import IUnitOfWork
from src.application.dtos.responses import TimelineResponse, ChangeEventResponse
from src.domain.value_objects.repository_id import RepositoryId

class GetRepositoryTimelineUseCase:
    """Retrieves the history timeline of a repository sorted chronologically."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(self, repository_id: str) -> List[TimelineResponse]:
        """Fetch all commits and group their change events into a timeline."""
        repo_id = RepositoryId(uuid.UUID(repository_id))
        with self.uow_factory() as uow:
            # Get all commits chronologically
            commits = uow.commits.list_by_repository(repo_id)
            
            timeline = []
            for c in commits:
                events = uow.change_events.get_by_commit(c.hash)
                changes_dto = [
                    ChangeEventResponse(
                        id=str(e.id),
                        repository_id=str(e.repository_id),
                        commit_hash=e.commit_hash,
                        seid=str(e.seid),
                        change_type=e.change_type.value,
                        metadata=e.metadata
                    )
                    for e in events
                ]
                
                timeline.append(
                    TimelineResponse(
                        commit_hash=c.hash,
                        timestamp=c.timestamp,
                        message=c.message,
                        changes=changes_dto
                    )
                )
                
            return timeline
