"""
Phase 7A — ReasoningArtifactService

Converts a ``ReasoningResult`` into a ``KnowledgeArtifact`` and persists it
via the Unit of Work so that reasoning outputs participate in the same
temporal versioning system as all other platform knowledge.

KnowledgeArtifact mapping
--------------------------
  artifact_type = "reasoning"
  source        = "reasoning"
  confidence    = result.confidence.score
  provenance    = result.to_dict()  (full auditable payload)
  valid_from_commit = snapshot.commit_hash (or "unknown")
  valid_to_commit   = None  (open-ended until superseded)
  artifact_version  = 1

Why persist reasoning results?
-------------------------------
* Enables **temporal queries**: "What did we conclude about X at commit Y?"
* Enables **result diffing**: compare reasoning at two different commits.
* Enables **governance audits**: show what reasoning was running when.
* Phase 8 query UI can fetch these instead of re-executing expensive queries.
"""

from __future__ import annotations

import uuid
import logging
from datetime import datetime

from src.domain.entities.knowledge_artifact import KnowledgeArtifact
from src.application.reasoning.reasoning_result import ReasoningResult
from src.application.ports.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


class ReasoningArtifactService:
    """Converts and persists ``ReasoningResult`` as ``KnowledgeArtifact``."""

    def save(self, result: ReasoningResult, uow: IUnitOfWork) -> KnowledgeArtifact:
        """Persist *result* as a KnowledgeArtifact and return the saved entity.

        Args:
            result: Completed reasoning result to persist.
            uow:    Open Unit of Work (caller manages commit).

        Returns:
            The saved :class:`KnowledgeArtifact` entity.
        """
        commit_hash = "unknown"
        if result.snapshot:
            commit_hash = result.snapshot.commit_hash or "unknown"

        repository_id_str = ""
        if result.snapshot:
            repository_id_str = result.snapshot.repository_id
        if not repository_id_str and result.evidence:
            # Fallback: try to extract from first evidence metadata
            repository_id_str = str(
                result.evidence[0].metadata.get("repository_id", "")
            )

        try:
            repo_uuid = uuid.UUID(str(repository_id_str))
        except (ValueError, AttributeError):
            repo_uuid = uuid.uuid4()
            logger.warning(
                "ReasoningArtifactService: could not parse repository_id=%r; "
                "generated new UUID %s.",
                repository_id_str,
                repo_uuid,
            )

        artifact = KnowledgeArtifact(
            id=uuid.uuid4(),
            repository_id=repo_uuid,
            artifact_type="reasoning",
            source="reasoning",
            confidence=result.confidence.score,
            valid_from_commit=commit_hash,
            valid_to_commit=None,
            observed_at=result.generated_at or datetime.utcnow(),
            artifact_version=1,
            provenance=result.to_dict(),
        )

        try:
            artifact.validate()
            uow.knowledge_artifacts.save(artifact)
            logger.info(
                "ReasoningArtifactService: saved artifact id=%s for execution_id=%s.",
                artifact.id,
                result.execution_id,
            )
        except Exception as exc:
            logger.error(
                "ReasoningArtifactService: failed to save artifact for "
                "execution_id=%s: %s",
                result.execution_id,
                exc,
            )
            raise

        return artifact
