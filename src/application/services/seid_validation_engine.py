"""Validation engine to assert SEID (Stable Entity ID) stability and continuity."""

import logging
from typing import Dict, List, Any

from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId

logger = logging.getLogger(__name__)

class SEIDValidationEngine:
    """Verifies SEID stability, identity continuity, and link integrity across commits."""

    def validate_seid_stability(self, uow: IUnitOfWork, repository_id: RepositoryId) -> Dict[str, Any]:
        """Runs checks to verify that SEID mappings are stable and unbroken."""
        errors: List[str] = []

        code_entities = uow.code_entities.get_by_repository(repository_id)
        entity_seids = {e.seid for e in code_entities}

        commits = uow.commits.list_by_repository(repository_id)

        # 1. Parent Link Integrity: every parent_seid must exist in entity_seids
        for entity in code_entities:
            if entity.parent_seid and entity.parent_seid not in entity_seids:
                errors.append(
                    f"Entity {entity.seid} has non-existent parent_seid {entity.parent_seid}"
                )

        # 2. Check for version gaps / ordinal skips (Link Integrity)
        for entity in code_entities:
            versions = uow.entity_versions.list_by_seid(entity.seid)
            if not versions:
                continue
            versions.sort(key=lambda x: x.version_ordinal)
            
            # Check contiguity
            for i in range(len(versions)):
                expected_ord = i + 1
                actual_ord = versions[i].version_ordinal
                if actual_ord != expected_ord:
                    errors.append(
                        f"SEID {entity.seid} has broken version ordinal chain: expected {expected_ord}, got {actual_ord}"
                    )
                    break

        # 3. Check for duplicates in active commit states
        from src.application.services.historical_reconstruction import HistoricalReconstructionService
        reconstruction_service = HistoricalReconstructionService()

        for c in commits:
            try:
                active_entities, _ = reconstruction_service.reconstruct_graph_at_commit(
                    uow, repository_id, c.hash
                )
                
                # Check for duplicate SEIDs
                seids_seen = set()
                for ent in active_entities:
                    if ent.seid in seids_seen:
                        errors.append(
                            f"Commit {c.hash} has duplicate active SEID {ent.seid}"
                        )
                    seids_seen.add(ent.seid)
            except Exception as e:
                errors.append(f"Failed to reconstruct graph at commit {c.hash}: {str(e)}")

        status = "PASSED" if not errors else "FAILED"
        return {
            "status": status,
            "errors": errors
        }
