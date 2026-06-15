"""Integration tests for Phase 6 capability blast radius."""

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

def test_capability_blast_radius_endpoint(api_client):
    container = api_client.app.state.container
    session = container.session_factory()
    uow = SQLAlchemyUnitOfWork(DummyEngine(session))

    repo_id = RepositoryId.generate()
    cap_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    # 1. Seed capability in database
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
            name="Auth Services",
            description="Authentication system",
            confidence=0.92,
            capability_type="SECURITY",
            maturity_score=0.8,
            risk_score=0.2,
            coverage_score=0.9,
            concepts=[],
            behaviors=[],
            flows=[],
            entities=[],
            relationships=[],
            coverage={}
        )
        uow._session.add(cap)
        uow.commit()

    # 2. Query blast radius API
    resp = api_client.get(f"/api/v1/capabilities/{cap_id}/blast-radius")
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["capability_id"] == str(cap_id)
    assert "blast_radius_score" in res_data
    assert "impacted_capability_ids" in res_data
