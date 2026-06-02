"""Use case for fetching entity version history."""

from typing import Callable, List
import uuid

from src.application.ports.unit_of_work import IUnitOfWork
from src.application.dtos.responses import EntityVersionResponse
from src.domain.value_objects.entity_id import SEID

class GetEntityHistoryUseCase:
    """Retrieves the history timeline of an entity by its SEID."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(self, seid_str: str) -> List[EntityVersionResponse]:
        """Fetch all versions of the given SEID."""
        entity_seid = SEID.from_string(seid_str)
        with self.uow_factory() as uow:
            versions = uow.entity_versions.list_by_seid(entity_seid)
            
            return [
                EntityVersionResponse(
                    id=str(v.id),
                    seid=str(v.seid),
                    commit_hash=v.commit_hash,
                    version_ordinal=v.version_ordinal,
                    mutation_type=v.mutation_type.value,
                    canonical_name=v.canonical_name,
                    file_path=v.file_path,
                    start_line=v.start_line,
                    end_line=v.end_line,
                    content_hash=v.content_hash,
                    structural_fingerprint=v.structural_fingerprint,
                    source_text=v.source_text,
                    metadata=v.metadata
                )
                for v in versions
            ]
