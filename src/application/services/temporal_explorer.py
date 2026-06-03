"""Explorer service for reading entity and relationship evolution timelines."""

import logging
import datetime
from typing import List, Dict, Any

from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId

logger = logging.getLogger(__name__)

class TemporalExplorer:
    """Provides semantic read queries for structural evolution paths in temporal graphs."""

    def get_entity_evolution_timeline(self, uow: IUnitOfWork, seid: SEID) -> List[Dict[str, Any]]:
        """Retrieves the chronological lifecycle version sequence of a specific entity."""
        versions = uow.entity_versions.list_by_seid(seid)
        versions.sort(key=lambda x: x.version_ordinal)

        timeline = []
        for ev in versions:
            timeline.append({
                "version_ordinal": ev.version_ordinal,
                "commit_hash": ev.commit_hash,
                "mutation_type": ev.mutation_type.name,
                "canonical_name": ev.canonical_name,
                "file_path": ev.file_path,
                "start_line": ev.start_line,
                "end_line": ev.end_line,
                "confidence": ev.confidence
            })
        return timeline

    def get_relationship_evolution_timeline(self, uow: IUnitOfWork, relationship_id: str) -> List[Dict[str, Any]]:
        """Retrieves changes and version updates for a specific relationship."""
        import uuid
        try:
            rel_uuid = uuid.UUID(relationship_id)
        except ValueError:
            return []

        versions = uow.relationship_versions.list_by_relationship(rel_uuid)
        # Sort by commit chronological timestamp via database commits list if needed, or by commit hash
        # To order them properly, let's look up commits of relationship versions
        versions_with_commits = []
        for rv in versions:
            commit = uow.commits.get_by_hash(rv.commit_hash)
            timestamp = commit.timestamp if commit else datetime.datetime.fromtimestamp(0, datetime.timezone.utc)
            versions_with_commits.append((timestamp, rv))

        versions_with_commits.sort(key=lambda x: x[0])

        timeline = []
        for timestamp, rv in versions_with_commits:
            timeline.append({
                "commit_hash": rv.commit_hash,
                "mutation_type": rv.mutation_type.name,
                "confidence": rv.confidence,
                "timestamp": timestamp
            })
        return timeline
