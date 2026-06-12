"""Integration tests for ReconstructionValidationEngine."""

import datetime
import uuid
import pytest
from unittest.mock import MagicMock

from src.domain.entities.commit import Commit
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.relationship import Relationship
from src.domain.entities.entity_version import EntityVersion
from src.domain.entities.relationship_version import RelationshipVersion
from src.domain.entities.repository import RepositoryEntity
from src.domain.enums.mutation_type import MutationType
from src.domain.enums.entity_type import EntityType
from src.domain.enums.relationship_type import RelationshipType
from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.application.services.historical_reconstruction import HistoricalReconstructionService
from src.application.services.reconstruction_validation_engine import ReconstructionValidationEngine
from src.domain.enums.analysis_status import AnalysisStatus

class DummyEngine:
    def __init__(self, session):
        self.session_factory = lambda: session

def test_reconstruction_validation_accuracy_calculation(db_session):
    repo_id = RepositoryId.generate()
    uow = SQLAlchemyUnitOfWork(DummyEngine(db_session))
    
    # 1. Database Setup: Create repository, commits, code entities and versions
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
        
        commit = Commit("hash1", repo_id, "Auth", "email", now, "C1", [])
        uow.commits.save(commit)
        
        # Entity 1 (will match between DB and checkout)
        seid_match = SEID.generate()
        file_id = FileId(uuid.uuid4())
        entity_match = CodeEntity(
            seid=seid_match,
            entity_type=EntityType.FUNCTION,
            name="match_func",
            qualified_name="match_func",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=CodeLocation("src/file.py", 1, 5, 0, 0)
        )
        uow.code_entities.save(entity_match)
        
        ev_match = EntityVersion(
            id=uuid.uuid4(),
            seid=seid_match,
            commit_hash="hash1",
            version_ordinal=1,
            mutation_type=MutationType.CREATED,
            canonical_name="match_func",
            file_path="src/file.py",
            start_line=1,
            end_line=5,
            content_hash="h1",
            structural_fingerprint="fp1"
        )
        uow.entity_versions.save(ev_match)
        
        # Entity 2 (in DB but missing from checkout)
        seid_missing = SEID.generate()
        entity_missing = CodeEntity(
            seid=seid_missing,
            entity_type=EntityType.FUNCTION,
            name="missing_func",
            qualified_name="missing_func",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=CodeLocation("src/file.py", 10, 15, 0, 0)
        )
        uow.code_entities.save(entity_missing)
        
        ev_missing = EntityVersion(
            id=uuid.uuid4(),
            seid=seid_missing,
            commit_hash="hash1",
            version_ordinal=1,
            mutation_type=MutationType.CREATED,
            canonical_name="missing_func",
            file_path="src/file.py",
            start_line=10,
            end_line=15,
            content_hash="h2",
            structural_fingerprint="fp2"
        )
        uow.entity_versions.save(ev_missing)

        uow.commit()

    # 2. Mock infrastructure dependencies
    reconstruction_service = HistoricalReconstructionService()
    
    git_adapter = MagicMock()
    file_scanner = MagicMock()
    
    # Mock files scanned
    mock_file = MagicMock()
    mock_file.absolute_path = "src/file.py"
    mock_file.path = "src/file.py"
    mock_file.language = SupportedLanguage.PYTHON
    mock_file.size_bytes = 100
    file_scanner.scan_repository.return_value = [mock_file]
    
    parser = MagicMock()
    entity_extractor = MagicMock()
    relationship_extractor = MagicMock()
    
    # Set up ground truth extraction:
    # Ground truth contains:
    # - entity_match (matching with DB)
    # - entity_extra (new entity not present in DB)
    seid_extra = SEID.generate()
    entity_extra = CodeEntity(
        seid=seid_extra,
        entity_type=EntityType.FUNCTION,
        name="extra_func",
        qualified_name="extra_func",
        file_id=file_id,
        repository_id=repo_id,
        parent_seid=None,
        language=SupportedLanguage.PYTHON,
        location=CodeLocation("src/file.py", 20, 25, 0, 0)
    )
    entity_extractor.extract.return_value = ([entity_match, entity_extra], None)
    relationship_extractor.extract.return_value = []
    
    identity_service = MagicMock()
    identity_service.compute_content_hash.return_value = "h1"

    engine = ReconstructionValidationEngine(
        reconstruction_service=reconstruction_service,
        git_adapter=git_adapter,
        file_scanner=file_scanner,
        parser=parser,
        entity_extractor=entity_extractor,
        relationship_extractor=relationship_extractor,
        identity_service=identity_service
    )

    from unittest.mock import patch, mock_open
    with uow:
        # Run validation
        with patch("builtins.open", mock_open(read_data="def match_func(): pass")):
            report = engine.verify_reconstruction_accuracy(uow, repo_id, "hash1", restore_branch="main")
        
        # Verify Git actions called
        git_adapter.checkout_commit.assert_any_call("src/", "hash1")
        git_adapter.checkout_commit.assert_any_call("src/", "main")
        
        # Check computed metrics:
        # Ground truth has: entity_match, entity_extra (Total actual = 2)
        # Database reconstruction has: entity_match, entity_missing (Total reconstructed = 2)
        # Matches: entity_match (Matching count = 1)
        # Reconstruction accuracy = 1 / 2 = 0.50
        assert report.reconstruction_accuracy == 0.5
        assert report.commit_hash == "hash1"
        
        # Verify saved in database
        saved_report = uow.metrics.get_accuracy_report_by_commit(repo_id, "hash1")
        assert saved_report is not None
        assert saved_report.reconstruction_accuracy == 0.5
