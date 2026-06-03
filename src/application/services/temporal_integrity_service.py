"""Service to audit and repair structural integrity issues in the temporal graph."""

import datetime
import logging
import uuid
from typing import List, Dict, Any

from sqlalchemy import select, delete

from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.entities.integrity import IntegrityViolation, RepairAudit
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.entity_id import SEID
from src.infrastructure.persistence.models.entity_version_model import EntityVersionModel
from src.infrastructure.persistence.models.relationship_version_model import RelationshipVersionModel
from src.infrastructure.persistence.models.relationship_model import RelationshipModel
from src.infrastructure.persistence.models.snapshot_model import RepositorySnapshotModel
from src.infrastructure.persistence.models.integrity_model import IntegrityViolationModel

logger = logging.getLogger(__name__)

class TemporalIntegrityService:
    """Audits and repairs database structural consistency issues for temporal graphs."""

    def perform_integrity_check(self, uow: IUnitOfWork, repository_id: RepositoryId) -> List[IntegrityViolation]:
        """Scans the database tables for structural consistency violations."""
        session = uow._session
        
        # 1. Clear existing violations for this repository to avoid duplicates
        session.execute(
            delete(IntegrityViolationModel).where(IntegrityViolationModel.repository_id == repository_id.value)
        )
        session.flush()

        violations: List[IntegrityViolation] = []
        now = datetime.datetime.now(datetime.timezone.utc)

        # Retrieve all active entities and relationships
        code_entities = uow.code_entities.get_by_repository(repository_id)
        valid_seids = {e.seid for e in code_entities}
        valid_seids_str = {str(e.seid.value) for e in code_entities}

        relationships = uow.relationships.get_by_repository(repository_id)
        valid_rel_ids = {r.id for r in relationships}

        commits = uow.commits.list_by_repository(repository_id)
        commit_hashes = [c.hash for c in commits]

        # ----------------------------------------------------
        # Check 1: Orphan Versions (EntityVersion & RelationshipVersion)
        # ----------------------------------------------------
        for commit_hash in commit_hashes:
            evs = uow.entity_versions.get_by_commit(commit_hash)
            for ev in evs:
                if ev.seid not in valid_seids:
                    violations.append(
                        IntegrityViolation(
                            id=uuid.uuid4(),
                            repository_id=repository_id,
                            violation_type="ORPHAN_ENTITY_VERSION",
                            severity="ERROR",
                            target_seid=str(ev.seid.value),
                            description=f"EntityVersion {ev.id} references non-existent SEID {ev.seid}",
                            recommended_repair="DELETE",
                            is_resolved=False,
                            detected_at=now
                        )
                    )

            rvs = uow.relationship_versions.get_by_commit(commit_hash)
            for rv in rvs:
                if rv.relationship_id not in valid_rel_ids:
                    violations.append(
                        IntegrityViolation(
                            id=uuid.uuid4(),
                            repository_id=repository_id,
                            violation_type="ORPHAN_RELATIONSHIP_VERSION",
                            severity="ERROR",
                            target_seid=str(rv.relationship_id),
                            description=f"RelationshipVersion {rv.id} references non-existent Relationship ID {rv.relationship_id}",
                            recommended_repair="DELETE",
                            is_resolved=False,
                            detected_at=now
                        )
                    )

        # ----------------------------------------------------
        # Check 2: Dangling Relationship Edges
        # ----------------------------------------------------
        for r in relationships:
            if r.source_seid not in valid_seids:
                violations.append(
                    IntegrityViolation(
                        id=uuid.uuid4(),
                        repository_id=repository_id,
                        violation_type="DANGLING_RELATIONSHIP_SOURCE",
                        severity="ERROR",
                        target_seid=str(r.source_seid.value),
                        description=f"Relationship {r.id} references non-existent source SEID {r.source_seid}",
                        recommended_repair="DELETE",
                        is_resolved=False,
                        detected_at=now
                    )
                )
            if r.target_seid not in valid_seids:
                violations.append(
                    IntegrityViolation(
                        id=uuid.uuid4(),
                        repository_id=repository_id,
                        violation_type="DANGLING_RELATIONSHIP_TARGET",
                        severity="ERROR",
                        target_seid=str(r.target_seid.value),
                        description=f"Relationship {r.id} references non-existent target SEID {r.target_seid}",
                        recommended_repair="DELETE",
                        is_resolved=False,
                        detected_at=now
                    )
                )

        # ----------------------------------------------------
        # Check 3: Ordinal Gaps
        # ----------------------------------------------------
        for entity in code_entities:
            versions = uow.entity_versions.list_by_seid(entity.seid)
            if not versions:
                continue
            versions.sort(key=lambda x: x.version_ordinal)
            
            # Check starts at 1
            if versions[0].version_ordinal != 1:
                violations.append(
                    IntegrityViolation(
                        id=uuid.uuid4(),
                        repository_id=repository_id,
                        violation_type="ORDINAL_GAP",
                        severity="WARNING",
                        target_seid=str(entity.seid.value),
                        description=f"Entity {entity.seid} version sequence starts at {versions[0].version_ordinal} instead of 1",
                        recommended_repair="REORDER",
                        is_resolved=False,
                        detected_at=now
                    )
                )
            else:
                # Check contiguity
                for i in range(len(versions) - 1):
                    current_ord = versions[i].version_ordinal
                    next_ord = versions[i+1].version_ordinal
                    if next_ord != current_ord + 1:
                        violations.append(
                            IntegrityViolation(
                                id=uuid.uuid4(),
                                repository_id=repository_id,
                                violation_type="ORDINAL_GAP",
                                severity="WARNING",
                                target_seid=str(entity.seid.value),
                                description=f"Entity {entity.seid} has version ordinal gap: {current_ord} -> {next_ord}",
                                recommended_repair="REORDER",
                                is_resolved=False,
                                detected_at=now
                            )
                        )
                        break

        # ----------------------------------------------------
        # Check 4: Corrupt Snapshots
        # ----------------------------------------------------
        stmt = select(RepositorySnapshotModel).where(RepositorySnapshotModel.repository_id == repository_id.value)
        snapshot_models = session.execute(stmt).scalars().all()
        for snap_m in snapshot_models:
            snap_data = snap_m.snapshot_data or {}
            entities_in_snap = snap_data.get("entities", [])
            rels_in_snap = snap_data.get("relationships", [])

            corrupt_elements = []
            for ent_ref in entities_in_snap:
                ent_seid_str = ent_ref.get("seid")
                if ent_seid_str not in valid_seids_str:
                    corrupt_elements.append(f"entity:{ent_seid_str}")

            for rel_ref in rels_in_snap:
                rel_id_str = rel_ref.get("id")
                try:
                    rel_uuid = uuid.UUID(rel_id_str)
                    if rel_uuid not in valid_rel_ids:
                        corrupt_elements.append(f"relationship:{rel_id_str}")
                except Exception:
                    corrupt_elements.append(f"relationship:invalid_uuid:{rel_id_str}")

            if corrupt_elements:
                violations.append(
                    IntegrityViolation(
                        id=uuid.uuid4(),
                        repository_id=repository_id,
                        violation_type="CORRUPT_SNAPSHOT",
                        severity="WARNING",
                        target_seid=None,
                        description=f"Snapshot at commit {snap_m.commit_hash} contains invalid references: {', '.join(corrupt_elements)}",
                        recommended_repair="REGENERATE",
                        is_resolved=False,
                        detected_at=now
                    )
                )

        # Persist violations
        if violations:
            uow.integrity.save_violations_batch(violations)

        return violations

    def get_repair_recipe(self, violations: List[IntegrityViolation]) -> Dict[str, Any]:
        """Generates dry-run repair action recipes from violations."""
        recipe_actions = []
        for v in violations:
            recipe_actions.append({
                "violation_id": str(v.id),
                "violation_type": v.violation_type,
                "target_seid": v.target_seid,
                "action": v.recommended_repair,
                "description": v.description
            })
        return {"actions": recipe_actions}

    def execute_repairs(self, uow: IUnitOfWork, repository_id: RepositoryId, violation_ids: List[uuid.UUID], operator: str) -> RepairAudit:
        """Executes repairs for specified violation IDs in a transaction."""
        session = uow._session
        
        violations_to_resolve: List[IntegrityViolation] = []
        for vid in violation_ids:
            violation = uow.integrity.get_violation_by_id(vid)
            if violation and not violation.is_resolved:
                violations_to_resolve.append(violation)

        repair_actions = []

        for v in violations_to_resolve:
            action_taken = {
                "violation_id": str(v.id),
                "violation_type": v.violation_type,
                "repair_type": v.recommended_repair,
                "details": {}
            }

            if v.violation_type == "ORPHAN_ENTITY_VERSION":
                # Find matching EntityVersionModel(s) and delete
                # Description pattern: "EntityVersion {ev.id} references..."
                # Let's extract UUID or search by SEID
                parts = v.description.split()
                ev_id_str = parts[1]
                try:
                    ev_id = uuid.UUID(ev_id_str)
                    session.execute(
                        delete(EntityVersionModel).where(EntityVersionModel.id == ev_id)
                    )
                    action_taken["details"] = {"deleted_entity_version_id": ev_id_str}
                except Exception as ex:
                    logger.error(f"Failed to parse or delete EntityVersion {ev_id_str}: {ex}")

            elif v.violation_type == "ORPHAN_RELATIONSHIP_VERSION":
                parts = v.description.split()
                rv_id_str = parts[1]
                try:
                    rv_id = uuid.UUID(rv_id_str)
                    session.execute(
                        delete(RelationshipVersionModel).where(RelationshipVersionModel.id == rv_id)
                    )
                    action_taken["details"] = {"deleted_relationship_version_id": rv_id_str}
                except Exception as ex:
                    logger.error(f"Failed to parse or delete RelationshipVersion {rv_id_str}: {ex}")

            elif v.violation_type in ("DANGLING_RELATIONSHIP_SOURCE", "DANGLING_RELATIONSHIP_TARGET"):
                # Description pattern: "Relationship {r.id} references..."
                parts = v.description.split()
                r_id_str = parts[1]
                try:
                    r_id = uuid.UUID(r_id_str)
                    session.execute(
                        delete(RelationshipModel).where(RelationshipModel.id == r_id)
                    )
                    action_taken["details"] = {"deleted_relationship_id": r_id_str}
                except Exception as ex:
                    logger.error(f"Failed to parse or delete Relationship {r_id_str}: {ex}")

            elif v.violation_type == "ORDINAL_GAP":
                # Reorder EntityVersion sequence starting from 1 for the target SEID
                if v.target_seid:
                    stmt = (
                        select(EntityVersionModel)
                        .where(EntityVersionModel.seid == uuid.UUID(v.target_seid))
                        .order_by(EntityVersionModel.version_ordinal.asc())
                    )
                    ev_models = session.execute(stmt).scalars().all()
                    old_ords = []
                    new_ords = []
                    for idx, ev_m in enumerate(ev_models, start=1):
                        old_ords.append(ev_m.version_ordinal)
                        ev_m.version_ordinal = idx
                        session.merge(ev_m)
                        new_ords.append(idx)
                    action_taken["details"] = {
                        "seid": v.target_seid,
                        "old_ordinals": old_ords,
                        "new_ordinals": new_ords
                    }

            elif v.violation_type == "CORRUPT_SNAPSHOT":
                # Regenerate / clean snapshot
                # We can just fetch the RepositorySnapshotModel and filter out the invalid items
                # Description pattern: "Snapshot at commit {commit_hash} contains invalid references..."
                # Let's extract commit hash from description
                parts = v.description.split()
                commit_hash = parts[3]
                stmt = select(RepositorySnapshotModel).where(
                    RepositorySnapshotModel.repository_id == repository_id.value,
                    RepositorySnapshotModel.commit_hash == commit_hash
                )
                snap_m = session.execute(stmt).scalar_one_or_none()
                if snap_m:
                    # Filter lists
                    code_entities = uow.code_entities.get_by_repository(repository_id)
                    valid_seids_str = {str(e.seid.value) for e in code_entities}
                    relationships = uow.relationships.get_by_repository(repository_id)
                    valid_rel_ids = {str(r.id) for r in relationships}

                    entities_in_snap = snap_m.snapshot_data.get("entities", [])
                    rels_in_snap = snap_m.snapshot_data.get("relationships", [])

                    clean_entities = [e for e in entities_in_snap if e.get("seid") in valid_seids_str]
                    clean_rels = [r for r in rels_in_snap if r.get("id") in valid_rel_ids]

                    snap_m.snapshot_data = {
                        "entities": clean_entities,
                        "relationships": clean_rels
                    }
                    session.merge(snap_m)
                    action_taken["details"] = {
                        "commit_hash": commit_hash,
                        "cleaned_entities_count": len(entities_in_snap) - len(clean_entities),
                        "cleaned_relationships_count": len(rels_in_snap) - len(clean_rels)
                    }

            # Update violation record
            violation_model = session.get(IntegrityViolationModel, v.id)
            if violation_model:
                violation_model.is_resolved = True
                session.merge(violation_model)

            repair_actions.append(action_taken)

        # Log RepairAudit
        audit = RepairAudit(
            id=uuid.uuid4(),
            repository_id=repository_id,
            operator=operator,
            issue_ids=violation_ids,
            repair_actions=repair_actions,
            executed_at=datetime.datetime.now(datetime.timezone.utc)
        )
        uow.integrity.save_repair_audit(audit)
        
        return audit
