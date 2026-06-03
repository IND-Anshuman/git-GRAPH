"""Integration tests for AccuracyEngine precision/recall metrics calculation."""

import datetime
import uuid
import pytest
from unittest.mock import MagicMock

from src.domain.entities.commit import Commit
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.change_event import ChangeEvent
from src.domain.entities.entity_version import EntityVersion
from src.domain.entities.repository import RepositoryEntity
from src.domain.entities.metrics import AccuracyReport
from src.domain.enums.mutation_type import MutationType
from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.application.services.accuracy_engine import AccuracyEngine
from src.domain.enums.analysis_status import AnalysisStatus

class DummyEngine:
    def __init__(self, session):
        self.session_factory = lambda: session

def test_accuracy_engine_precision_recall_calculation(db_session):
    repo_id = RepositoryId.generate()
    uow = SQLAlchemyUnitOfWork(DummyEngine(db_session))
    
    # 1. Database Setup: Create repository, commits, versions and change events
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
        commit2 = Commit("hash2", repo_id, "Auth", "email", now, "C2", ["hash1"])
        uow.commits.save(commit1)
        uow.commits.save(commit2)
        
        # Entity 1 (CREATED at hash1, RENAMED at hash2)
        seid1 = SEID.generate()
        file_id = FileId(uuid.uuid4())
        entity1 = CodeEntity(
            seid=seid1,
            entity_type=EntityType.FUNCTION,
            name="compute_tax",
            qualified_name="compute_tax",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=CodeLocation("src/tax.py", 1, 5, 0, 0)
        )
        uow.code_entities.save(entity1)
        
        ev1 = EntityVersion(
            id=uuid.uuid4(),
            seid=seid1,
            commit_hash="hash1",
            version_ordinal=1,
            mutation_type=MutationType.CREATED,
            canonical_name="calculate_tax", # old name
            file_path="src/tax.py",
            start_line=1,
            end_line=5,
            content_hash="h1",
            structural_fingerprint="fp1"
        )
        ev2 = EntityVersion(
            id=uuid.uuid4(),
            seid=seid1,
            commit_hash="hash2",
            version_ordinal=2,
            mutation_type=MutationType.RENAMED,
            canonical_name="compute_tax", # new name
            file_path="src/tax.py",
            start_line=1,
            end_line=5,
            content_hash="h1",
            structural_fingerprint="fp1"
        )
        uow.entity_versions.save(ev1)
        uow.entity_versions.save(ev2)
        
        ce1 = ChangeEvent(
            id=uuid.uuid4(),
            repository_id=repo_id,
            commit_hash="hash1",
            seid=seid1,
            change_type=MutationType.CREATED
        )
        ce2 = ChangeEvent(
            id=uuid.uuid4(),
            repository_id=repo_id,
            commit_hash="hash2",
            seid=seid1,
            change_type=MutationType.RENAMED
        )
        uow.change_events.save(ce1)
        uow.change_events.save(ce2)
        
        uow.commit()

    # 2. Setup mock ReconstructionValidationEngine
    validation_engine = MagicMock()
    mock_recon_report = MagicMock()
    mock_recon_report.reconstruction_accuracy = 0.95
    validation_engine.verify_reconstruction_accuracy.return_value = mock_recon_report

    engine = AccuracyEngine(validation_engine)

    # 3. Define Ground Truth Timeline:
    # Match rename exactly
    ground_truth_data = {
      "repository_name": "test-repo",
      "expected_timeline": [
        {
          "commit_hash": "hash1",
          "changes": [
            {
              "seid": "some-id",
              "change_type": "CREATED",
              "canonical_name": "calculate_tax",
              "file_path": "src/tax.py"
            }
          ]
        },
        {
          "commit_hash": "hash2",
          "changes": [
            {
              "seid": "some-id",
              "change_type": "RENAMED",
              "canonical_name": "compute_tax",
              "file_path": "src/tax.py",
              "previous_name": "calculate_tax",
              "previous_path": "src/tax.py"
            }
          ]
        }
      ]
    }

    with uow:
        # Evaluate Accuracy
        report = engine.evaluate_accuracy(uow, repo_id, ground_truth_data, target_commit_hash="hash2")
        
        # Expected rename match: ("hash2", "compute_tax")
        # predicted_renames = {("hash2", "compute_tax")}
        # expected_renames = {("hash2", "compute_tax")}
        # rename precision = 1.0, rename recall = 1.0
        assert report.rename_precision == 1.0
        assert report.rename_recall == 1.0
        assert report.move_precision == 1.0 # default to 1.0 since no moves predicted/expected
        assert report.event_accuracy == 1.0
        assert report.reconstruction_accuracy == 0.95
        
        # Verify saved in DB
        saved_report = uow.metrics.get_accuracy_report_by_commit(repo_id, "hash2")
        assert saved_report is not None
        assert saved_report.reconstruction_accuracy == 0.95
