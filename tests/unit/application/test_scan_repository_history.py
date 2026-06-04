import uuid
import datetime
from unittest.mock import MagicMock, patch
import pytest

from src.application.use_cases.scan_repository_history import ScanRepositoryHistoryUseCase
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.entities.repository import RepositoryEntity
from src.domain.entities.commit import Commit
from src.domain.enums.analysis_status import AnalysisStatus
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork

class DummyEngine:
    def __init__(self, session):
        self.session_factory = lambda: session

@patch("src.application.use_cases.scan_repository_history.CommitWalker")
def test_scan_history_telemetry_benchmark_saved(mock_commit_walker_cls, db_session):
    repo_id = RepositoryId.generate()
    repo_uuid = repo_id.value

    # Prepare repository in DB
    now = datetime.datetime.now(datetime.timezone.utc)
    uow_factory = lambda: SQLAlchemyUnitOfWork(DummyEngine(db_session))
    
    with uow_factory() as uow:
        repo = RepositoryEntity(
            id=repo_id,
            url="https://github.com/user/repo",
            name="test-repo",
            default_branch="main",
            local_path="/tmp/repo",
            status=AnalysisStatus.PENDING,
            created_at=now,
            updated_at=now
        )
        uow.repositories.save(repo)
        uow.commit()

    # Mock walker to return a single commit
    mock_walker = MagicMock()
    mock_commit = Commit("hash1", repo_id, "Author", "email", now, "Msg", [])
    mock_walker.walk_history.return_value = [(mock_commit, [])]
    mock_commit_walker_cls.return_value = mock_walker

    # Other mocks
    git_adapter = MagicMock()
    file_scanner = MagicMock()
    file_scanner.scan_repository.return_value = []
    parser = MagicMock()
    entity_extractor = MagicMock()
    relationship_extractor = MagicMock()
    identity_service = MagicMock()
    
    diff_engine = MagicMock()
    diff_result = MagicMock()
    diff_result.entities_to_save = []
    diff_result.versions_to_save = []
    diff_result.relationships_to_save = []
    diff_result.relationship_versions_to_save = []
    diff_result.change_events_to_save = []
    diff_engine.compute_diff.return_value = diff_result

    reconstruction_service = MagicMock()
    reconstruction_service.reconstruct_graph_at_commit.return_value = ([], [])

    use_case = ScanRepositoryHistoryUseCase(
        git_adapter=git_adapter,
        file_scanner=file_scanner,
        parser=parser,
        entity_extractor=entity_extractor,
        relationship_extractor=relationship_extractor,
        diff_engine=diff_engine,
        uow_factory=uow_factory,
        identity_service=identity_service,
        reconstruction_service=reconstruction_service
    )

    # Execute
    res = use_case.execute(repo_uuid)

    assert res["status"] == "success"
    assert res["processed_commits"] == 1

    # Verify a BenchmarkReport is stored in the database for the commit
    with uow_factory() as uow:
        benchmarks = uow.metrics.list_benchmark_reports(repo_id)
        assert len(benchmarks) == 1
        report = benchmarks[0]
        assert report.commit_hash == "hash1"
        assert report.scan_duration_ms >= 0
        assert report.diff_throughput_nodes_sec == 0.0
        assert report.memory_rss_bytes >= 0
        assert report.db_size_bytes >= 0
