"""Integration tests for Phase 6 capability discovery and listing."""

import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app
from src.infrastructure.persistence.models import Base
from src.domain.entities.repository import RepositoryEntity
from src.domain.entities.commit import Commit
from src.domain.entities.concept_node import ConceptNode
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.value_objects.repository_id import RepositoryId
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.infrastructure.persistence.models.capability_models import (
    CapabilityModel,
    CapabilityCandidateModel,
)

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

def test_capability_discovery_and_governance(api_client):
    container = api_client.app.state.container
    session = container.session_factory()
    uow = SQLAlchemyUnitOfWork(DummyEngine(session))

    repo_id = RepositoryId.generate()
    now = datetime.now(timezone.utc)

    # 1. Seed repository, commit, and a concept node
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
            metadata={"last_analyzed_commit": "hash2"}
        )
        uow.repositories.save(repo)

        commit1 = Commit("hash1", repo_id, "Auth", "email", now, "C1", [])
        uow.commits.save(commit1)

        c_node = ConceptNode(
            id=uuid.uuid4(),
            repository_id=repo_id,
            ontology_node_id="security.authentication.login",
            name="Authentication Login",
            description="Auth module",
            is_system_defined=True,
            created_at=now,
            updated_at=now
        )
        uow.concept_nodes.save(c_node)
        uow.commit()

    # 2. Trigger automated discovery
    discover_resp = api_client.post(f"/api/v1/repositories/{repo_id.value}/capabilities/discover")
    assert discover_resp.status_code == 200
    candidates = discover_resp.json()
    assert len(candidates) > 0
    candidate = candidates[0]
    assert candidate["status"] == "CANDIDATE"

    # 3. Retrieve candidates
    list_cand_resp = api_client.get(f"/api/v1/repositories/{repo_id.value}/capabilities/candidates")
    assert list_cand_resp.status_code == 200
    assert len(list_cand_resp.json()) == len(candidates)

    # 4. Approve candidate
    candidate_id = candidate["id"]
    approve_resp = api_client.post(f"/api/v1/capabilities/{candidate_id}/approve")
    assert approve_resp.status_code == 200
    approved_cap = approve_resp.json()
    assert approved_cap["id"] == candidate_id
    assert approved_cap["name"] == candidate["name"]

    # 5. Retrieve approved capabilities
    list_caps_resp = api_client.get(f"/api/v1/repositories/{repo_id.value}/capabilities")
    assert list_caps_resp.status_code == 200
    assert len(list_caps_resp.json()) == 1
    assert list_caps_resp.json()[0]["id"] == candidate_id

    # 6. Retrieve single approved capability
    get_cap_resp = api_client.get(f"/api/v1/capabilities/{candidate_id}")
    assert get_cap_resp.status_code == 200
    assert get_cap_resp.json()["id"] == candidate_id

    # 7. Query capabilities semantically
    query_resp = api_client.post(
        f"/api/v1/repositories/{repo_id.value}/capabilities/query",
        json={"query_text": "security", "limit": 5}
    )
    assert query_resp.status_code == 200
    results = query_resp.json()["results"]
    assert len(results) > 0
    assert results[0]["capability"]["id"] == candidate_id
