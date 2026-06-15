"""Integration tests for Phase 6 capability dependency graph."""

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

def test_capability_dependency_graph_builder(api_client):
    container = api_client.app.state.container
    session = container.session_factory()
    uow = SQLAlchemyUnitOfWork(DummyEngine(session))

    repo_id = RepositoryId.generate()
    now = datetime.now(timezone.utc)

    # 1. Seed repository
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
        uow.commit()

    # 2. Build dependency graph
    graph = container.capability_dependency_graph.build_dependency_graph(uow, repo_id.value)
    assert "nodes" in graph
    assert "edges" in graph
