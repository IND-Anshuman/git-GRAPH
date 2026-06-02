"""Integration tests for temporal graph API endpoints."""

from fastapi.testclient import TestClient
import pytest

from src.config import settings
from src.main import app
from src.infrastructure.persistence.models import Base

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

def test_health_check_endpoint(api_client):
    response = api_client.get("/api/v1/health")
    assert response.status_code == 200

def test_list_commits_endpoint_returns_404_or_empty(api_client):
    # Generates a random repository ID
    repo_uuid = "00000000-0000-0000-0000-000000000000"
    response = api_client.get(f"/api/v1/repositories/{repo_uuid}/commits")
    assert response.status_code == 200
    assert response.json() == []

def test_get_invalid_commit_returns_404(api_client):
    response = api_client.get("/api/v1/commits/non_existent_commit_hash")
    assert response.status_code == 404
    assert "detail" in response.json()
