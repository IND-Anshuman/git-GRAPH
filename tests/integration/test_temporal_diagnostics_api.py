"""Integration tests for the temporal diagnostics API endpoints."""

import datetime
import uuid
import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app
from src.infrastructure.persistence.models import Base
from src.domain.entities.repository import RepositoryEntity
from src.domain.entities.commit import Commit
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.entity_version import EntityVersion
from src.domain.entities.integrity import IntegrityViolation
from src.domain.entities.metrics import BenchmarkReport
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.enums.mutation_type import MutationType
from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.code_location import CodeLocation

@pytest.fixture
def api_client():
    """Returns a FastAPI TestClient that triggers lifespan startup and shutdown."""
    original_url = settings.database_url
    settings.database_url = "sqlite:///:memory:"
    try:
        with TestClient(app) as client:
            Base.metadata.create_all(client.app.state.container.engine)
            yield client
    finally:
        settings.database_url = original_url

def test_diagnostics_endpoints_lifecycle(api_client):
    container = api_client.app.state.container
    uow_factory = container.get_uow_factory()

    repo_id = RepositoryId.generate()
    repo_uuid_str = str(repo_id.value)
    
    # Assert 404 for non-existent repository health
    response = api_client.get(f"/api/v1/repositories/{repo_uuid_str}/diagnostics/health")
    assert response.status_code == 404

    # Setup database records for a valid repository check
    now = datetime.datetime.now(datetime.timezone.utc)
    with uow_factory() as uow:
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
        
        # Commit
        commit = Commit("hash1", repo_id, "Auth", "email", now, "C1", [])
        uow.commits.save(commit)
        
        # Valid entity
        valid_seid = SEID.generate()
        file_id = FileId(uuid.uuid4())
        entity = CodeEntity(
            seid=valid_seid,
            entity_type=EntityType.FUNCTION,
            name="func",
            qualified_name="func",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=CodeLocation("src/file.py", 1, 5, 0, 0)
        )
        uow.code_entities.save(entity)
        
        # 1. Integrity check target: version with gap (starts at 2)
        ev = EntityVersion(
            id=uuid.uuid4(),
            seid=valid_seid,
            commit_hash="hash1",
            version_ordinal=2, # Ordinal Gap! Should start at 1
            mutation_type=MutationType.CREATED,
            canonical_name="func",
            file_path="src/file.py",
            start_line=1,
            end_line=5,
            content_hash="h1",
            structural_fingerprint="fp1"
        )
        uow.entity_versions.save(ev)

        # 2. Benchmark Report
        benchmark = BenchmarkReport(
            id=uuid.uuid4(),
            repository_id=repo_id,
            commit_hash="hash1",
            scan_duration_ms=150,
            diff_throughput_nodes_sec=250.0,
            reconstruction_latency_ms=45,
            db_size_bytes=4096,
            memory_rss_bytes=1024 * 1024 * 50,
            measured_at=now
        )
        uow.metrics.save_benchmark_report(benchmark)
        
        uow.commit()

    # 1. Test Health endpoint
    response = api_client.get(f"/api/v1/repositories/{repo_uuid_str}/diagnostics/health")
    assert response.status_code == 200
    data = response.json()
    assert "health_score" in data
    assert "status" in data

    # 2. Test Integrity endpoint (runs checks and yields 1 gap violation)
    response = api_client.get(f"/api/v1/repositories/{repo_uuid_str}/diagnostics/integrity")
    assert response.status_code == 200
    violations = response.json()
    assert len(violations) == 1
    assert violations[0]["violation_type"] == "ORDINAL_GAP"
    violation_id = violations[0]["id"]

    # 3. Test Repair endpoint
    payload = {
        "issue_ids": [violation_id],
        "operator": "api-test"
    }
    response = api_client.post(f"/api/v1/repositories/{repo_uuid_str}/diagnostics/repair", json=payload)
    assert response.status_code == 200
    audit_data = response.json()
    assert audit_data["operator"] == "api-test"
    assert len(audit_data["repair_actions"]) == 1
    assert audit_data["repair_actions"][0]["violation_type"] == "ORDINAL_GAP"

    # Verify violation is resolved
    response = api_client.get(f"/api/v1/repositories/{repo_uuid_str}/diagnostics/integrity?unresolved_only=true")
    assert response.status_code == 200
    assert len(response.json()) == 0

    # 4. Test Benchmark endpoint
    response = api_client.get(f"/api/v1/repositories/{repo_uuid_str}/diagnostics/benchmarks")
    assert response.status_code == 200
    benchmarks = response.json()
    assert len(benchmarks) == 1
    assert benchmarks[0]["commit_hash"] == "hash1"
