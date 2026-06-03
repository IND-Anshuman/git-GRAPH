"""Integration tests for TemporalIntegrityService structural validation and repair capabilities."""

import datetime
import uuid
import pytest

from src.domain.entities.commit import Commit
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.relationship import Relationship
from src.domain.entities.entity_version import EntityVersion
from src.domain.entities.relationship_version import RelationshipVersion
from src.domain.entities.repository import RepositoryEntity
from src.domain.entities.repository_snapshot import RepositorySnapshot
from src.domain.enums.mutation_type import MutationType
from src.domain.enums.entity_type import EntityType
from src.domain.enums.relationship_type import RelationshipType
from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.application.services.temporal_integrity_service import TemporalIntegrityService
from src.domain.enums.analysis_status import AnalysisStatus

class DummyEngine:
    def __init__(self, session):
        self.session_factory = lambda: session

def test_temporal_integrity_checks_and_repairs(db_session):
    repo_id = RepositoryId.generate()
    uow = SQLAlchemyUnitOfWork(DummyEngine(db_session))
    
    with uow:
        # Create a repository
        now = datetime.datetime.now(datetime.timezone.utc)
        repo = RepositoryEntity(
            id=repo_id,
            url="https://github.com/test/repo",
            name="test-repo",
            default_branch="main",
            local_path="src/",
            status=AnalysisStatus.COMPLETED,
            created_at=now,
            updated_at=now
        )
        uow.repositories.save(repo)
        
        # Create commits (hash1 and hash2)
        commit1 = Commit("hash1", repo_id, "Auth", "email", now, "C1", [])
        commit2 = Commit("hash2", repo_id, "Auth", "email", now, "C2", ["hash1"])
        uow.commits.save(commit1)
        uow.commits.save(commit2)
        
        # Create one valid entity
        valid_seid = SEID.generate()
        file_id = FileId(uuid.uuid4())
        entity = CodeEntity(
            seid=valid_seid,
            entity_type=EntityType.FUNCTION,
            name="valid_func",
            qualified_name="valid_func",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=CodeLocation("src/file.py", 1, 5, 0, 0)
        )
        uow.code_entities.save(entity)
        
        # 1. ORPHAN VERSION: Create an EntityVersion for a non-existent SEID
        orphan_seid = SEID.generate()
        ev_orphan = EntityVersion(
            id=uuid.uuid4(),
            seid=orphan_seid,
            commit_hash="hash1",
            version_ordinal=1,
            mutation_type=MutationType.CREATED,
            canonical_name="orphan_func",
            file_path="src/file.py",
            start_line=1,
            end_line=5,
            content_hash="hash",
            structural_fingerprint="fp"
        )
        uow.entity_versions.save(ev_orphan)
        
        # 2. DANGLING RELATIONSHIP: Create a relationship referencing non-existent target SEID
        dangling_rel = Relationship(
            id=uuid.uuid4(),
            repository_id=repo_id,
            relationship_type=RelationshipType.CALLS,
            source_seid=valid_seid,
            target_seid=orphan_seid
        )
        uow.relationships.save(dangling_rel)
        
        # 3. ORDINAL GAP: Create entity versions with gap (1, then 3) for valid entity
        ev1 = EntityVersion(
            id=uuid.uuid4(),
            seid=valid_seid,
            commit_hash="hash1",
            version_ordinal=1,
            mutation_type=MutationType.CREATED,
            canonical_name="valid_func",
            file_path="src/file.py",
            start_line=1,
            end_line=5,
            content_hash="h1",
            structural_fingerprint="fp1"
        )
        ev3 = EntityVersion(
            id=uuid.uuid4(),
            seid=valid_seid,
            commit_hash="hash2", # different commit hash to satisfy unique constraint
            version_ordinal=3, # gap here! ordinal should be 2
            mutation_type=MutationType.MODIFIED,
            canonical_name="valid_func",
            file_path="src/file.py",
            start_line=1,
            end_line=5,
            content_hash="h2",
            structural_fingerprint="fp2"
        )
        uow.entity_versions.save(ev1)
        uow.entity_versions.save(ev3)
        
        # 4. CORRUPT SNAPSHOT: Create a snapshot that points to non-existent entities
        snapshot = RepositorySnapshot(
            id=uuid.uuid4(),
            repository_id=repo_id,
            commit_hash="hash1",
            entity_seids=[valid_seid, orphan_seid],
            snapshot_data={
                "entities": [{"seid": str(valid_seid)}, {"seid": str(orphan_seid)}],
                "relationships": []
            },
            created_at=now
        )
        uow.snapshots.save(snapshot)
        
        uow.commit()

    service = TemporalIntegrityService()
    
    with uow:
        # Run integrity check
        violations = service.perform_integrity_check(uow, repo_id)
        
        # Assert violations detected:
        # - Orphan EntityVersion
        # - Dangling Relationship target
        # - Ordinal Gap for valid_seid
        # - Corrupt snapshot referring to orphan_seid
        v_types = {v.violation_type for v in violations}
        assert "ORPHAN_ENTITY_VERSION" in v_types
        assert "DANGLING_RELATIONSHIP_TARGET" in v_types
        assert "ORDINAL_GAP" in v_types
        assert "CORRUPT_SNAPSHOT" in v_types
        
        # Test recipe generation
        recipe = service.get_repair_recipe(violations)
        assert len(recipe["actions"]) == len(violations)
        
        # Let's execute the repairs
        violation_ids = [v.id for v in violations]
        audit = service.execute_repairs(uow, repo_id, violation_ids, operator="test-operator")
        uow.commit()
        
        assert len(audit.repair_actions) == len(violations)
        assert audit.operator == "test-operator"
        
        # Re-run check and verify all violations are either resolved/gone!
        post_violations = service.perform_integrity_check(uow, repo_id)
        # Note: Ordinal Gap should be fixed (reordered ordinals: 1, 3 -> 1, 2)
        # Orphan version deleted.
        # Dangling relationship deleted.
        # Corrupt snapshot cleaned.
        # So there should be no more violations!
        assert len(post_violations) == 0
        
        # Verify ordinal gap repair specifically worked: check valid_seid versions ordinals are 1, 2
        versions = uow.entity_versions.list_by_seid(valid_seid)
        assert len(versions) == 2
        ords = sorted([v.version_ordinal for v in versions])
        assert ords == [1, 2]
