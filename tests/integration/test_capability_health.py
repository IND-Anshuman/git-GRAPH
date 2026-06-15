"""Integration tests for Phase 6 capability health and risk analysis."""

import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app
from src.infrastructure.persistence.models import Base
from src.domain.entities.repository import RepositoryEntity
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.value_objects.repository_id import RepositoryId
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.infrastructure.persistence.models.capability_models import CapabilityModel

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

class DummyEngine:
    def __init__(self, session):
        self.session_factory = lambda: session

def test_capability_health_and_risk(api_client):
    container = api_client.app.state.container
    session = container.session_factory()
    uow = SQLAlchemyUnitOfWork(DummyEngine(session))

    repo_id = RepositoryId.generate()
    cap_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    # 1. Seed repository and capability in database
    with uow:
        repo = RepositoryEntity(
            id=repo_id,
            url="https://github.com/test/repo",
            name="test-repo",
            default_branch="main",
            local_path="src/",
            status=AnalysisStatus.COMPLETED,
            created_at=now,
            updated_at=now,
            metadata={}
        )
        uow.repositories.save(repo)

        cap = CapabilityModel(
            id=cap_id,
            repository_id=repo_id.value,
            name="Data Persistence",
            description="Database querying",
            confidence=0.88,
            capability_type="TECHNICAL",
            maturity_score=0.75,
            risk_score=0.3,
            coverage_score=0.85,
            concepts=[],
            behaviors=[],
            flows=[],
            entities=[],
            relationships=[],
            coverage={}
        )
        uow._session.add(cap)
        uow.commit()

    # 2. Query health-risk API
    resp = api_client.get(f"/api/v1/capabilities/{cap_id}/health-risk")
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["capability_id"] == str(cap_id)
    assert "health_score" in res_data
    assert "risk_score" in res_data
    assert "stability_score" in res_data
    assert "cohesion_score" in res_data
    assert "coupling_score" in res_data
    assert "boundary_strength" in res_data
