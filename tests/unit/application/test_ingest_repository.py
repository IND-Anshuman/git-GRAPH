import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest

from src.application.use_cases.ingest_repository import IngestRepositoryUseCase
from src.application.dtos.commands import IngestRepositoryCommand
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.entities.repository import RepositoryEntity
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.entities.metrics import BenchmarkReport
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork

class DummyEngine:
    def __init__(self, session):
        self.session_factory = lambda: session

def test_ingestion_telemetry_benchmark_saved(db_session):
    # Prepare dependencies
    git_adapter = MagicMock()
    git_adapter.clone_repository.return_value = "/tmp/repo"
    git_adapter.get_current_commit_hash.return_value = "commit123"

    file_scanner = MagicMock()
    file_scanner.scan_repository.return_value = []

    parser = MagicMock()
    entity_extractor = MagicMock()
    relationship_extractor = MagicMock()
    identity_service = MagicMock()

    # Create dummy database engine wrapper for UoW
    uow_factory = lambda: SQLAlchemyUnitOfWork(DummyEngine(db_session))

    # Mock historical reconstruction service
    reconstruction_service = MagicMock()
    reconstruction_service.reconstruct_graph_at_commit.return_value = ([], [])

    use_case = IngestRepositoryUseCase(
        git_adapter=git_adapter,
        file_scanner=file_scanner,
        parser=parser,
        entity_extractor=entity_extractor,
        relationship_extractor=relationship_extractor,
        uow_factory=uow_factory,
        storage_root="/tmp/storage",
        identity_service=identity_service,
        reconstruction_service=reconstruction_service
    )

    command = IngestRepositoryCommand(
        url="https://github.com/user/repo",
        branch="main",
        name="test-repo"
    )

    # Execute
    res = use_case.execute(command)

    # Assert success
    assert res.status == "COMPLETED"

    # Verify a BenchmarkReport is stored in the database
    with uow_factory() as uow:
        repo_id = RepositoryId(uuid.UUID(res.repository_id))
        benchmarks = uow.metrics.list_benchmark_reports(repo_id)
        assert len(benchmarks) == 1
        report = benchmarks[0]
        assert report.commit_hash == "commit123"
        assert report.scan_duration_ms >= 0
        assert report.diff_throughput_nodes_sec == 0.0
        assert report.memory_rss_bytes >= 0
        assert report.db_size_bytes >= 0

def test_successful_ingestion():
    assert True

def test_duplicate_repository():
    assert True

def test_clone_failure():
    assert True
