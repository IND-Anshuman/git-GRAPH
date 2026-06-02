"""Use case for fetching entity changes introduced in a commit."""

from typing import Callable, List

from src.application.ports.unit_of_work import IUnitOfWork
from src.application.dtos.responses import ChangeEventResponse

class GetCommitChangesUseCase:
    """Retrieves all ChangeEvents introduced by a specific commit."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(self, commit_hash: str) -> List[ChangeEventResponse]:
        """Fetch all change events for the given commit hash."""
        with self.uow_factory() as uow:
            events = uow.change_events.get_by_commit(commit_hash)
            return [
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
