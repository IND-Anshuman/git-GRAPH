"""Integration tests for SEIDValidationEngine testing SEID stability and link integrity."""

import datetime
import uuid
import pytest

from src.domain.entities.commit import Commit
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.entity_version import EntityVersion
from src.domain.entities.repository import RepositoryEntity
from src.domain.enums.mutation_type import MutationType
from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.application.services.seid_validation_engine import SEIDValidationEngine
from src.domain.enums.analysis_status import AnalysisStatus

class DummyEngine:
    def __init__(self, session):
        self.session_factory = lambda: session

def test_seid_validation_engine_success(db_session):
    repo_id = RepositoryId.generate()
    uow = SQLAlchemyUnitOfWork(DummyEngine(db_session))
    
    now = datetime.datetime.now(datetime.timezone.utc)
    with uow:
        # Repository
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
        
        # Commits
        commit1 = Commit("hash1", repo_id, "Auth", "email", now, "C1", [])
        uow.commits.save(commit1)
        
        # Entities
        seid1 = SEID.generate()
        file_id = FileId(uuid.uuid4())
        entity1 = CodeEntity(
            seid=seid1,
            entity_type=EntityType.FUNCTION,
            name="func1",
            qualified_name="func1",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=CodeLocation("src/file.py", 1, 5, 0, 0)
        )
        uow.code_entities.save(entity1)
        
        # Versions
        ev1 = EntityVersion(
            id=uuid.uuid4(),
            seid=seid1,
            commit_hash="hash1",
            version_ordinal=1,
            mutation_type=MutationType.CREATED,
            canonical_name="func1",
            file_path="src/file.py",
            start_line=1,
            end_line=5,
            content_hash="h1",
            structural_fingerprint="fp1"
        )
        uow.entity_versions.save(ev1)
        
        uow.commit()

    engine = SEIDValidationEngine()

    with uow:
        result = engine.validate_seid_stability(uow, repo_id)
        assert result["status"] == "PASSED"
        assert len(result["errors"]) == 0

def test_seid_validation_engine_failures(db_session):
    repo_id = RepositoryId.generate()
    uow = SQLAlchemyUnitOfWork(DummyEngine(db_session))
    
    now = datetime.datetime.now(datetime.timezone.utc)
    with uow:
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
        
        commit1 = Commit("hash1", repo_id, "Auth", "email", now, "C1", [])
        uow.commits.save(commit1)
        
        # 1. Invalid parent link: entity2 has a non-existent parent_seid
        seid2 = SEID.generate()
        file_id = FileId(uuid.uuid4())
        entity2 = CodeEntity(
            seid=seid2,
            entity_type=EntityType.FUNCTION,
            name="func2",
            qualified_name="func2",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=SEID.generate(), # non-existent parent
            language=SupportedLanguage.PYTHON,
            location=CodeLocation("src/file.py", 1, 5, 0, 0)
        )
        uow.code_entities.save(entity2)
        
        # 2. Broken version ordinal chain: version_ordinal = 2, but no version 1
        ev2 = EntityVersion(
            id=uuid.uuid4(),
            seid=seid2,
            commit_hash="hash1",
            version_ordinal=2, # Gap here!
            mutation_type=MutationType.CREATED,
            canonical_name="func2",
            file_path="src/file.py",
            start_line=1,
            end_line=5,
            content_hash="h1",
            structural_fingerprint="fp1"
        )
        uow.entity_versions.save(ev2)
        
        uow.commit()

    engine = SEIDValidationEngine()

    with uow:
        result = engine.validate_seid_stability(uow, repo_id)
        assert result["status"] == "FAILED"
        # There should be two errors:
        # - non-existent parent
        # - broken version ordinal chain
        err_msg = "".join(result["errors"])
        assert "parent_seid" in err_msg
        assert "broken version ordinal chain" in err_msg
