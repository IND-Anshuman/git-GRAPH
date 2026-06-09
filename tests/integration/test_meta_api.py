"""Integration tests for Phase 4.75 Meta-Ontology, Schema Registry, and Discovery REST API endpoints."""

import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app
from src.infrastructure.persistence.models import Base
from src.domain.entities.repository import RepositoryEntity
from src.domain.entities.source_file import SourceFile
from src.domain.entities.code_entity import CodeEntity
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.domain.value_objects.fingerprint import StructuralFingerprint
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


def test_meta_api_flow(api_client):
    # Retrieve container and database session
    container = api_client.app.state.container
    session = container.session_factory()
    uow = SQLAlchemyUnitOfWork(DummyEngine(session))

    # 1. Register Embedding Model via REST API
    model_payload = {
        "id": "test-vector-model-api",
        "model_name": "API Test Vector Model",
        "provider": "local",
        "dimensions": 128,
        "distance_metric": "cosine",
        "is_active": True,
    }
    response = api_client.post("/api/v1/meta/embeddings/models", json=model_payload)
    assert response.status_code == 201
    assert response.json()["id"] == "test-vector-model-api"
    assert response.json()["is_active"] is True

    # 2. Register Embedding Version
    version_payload = {
        "version_string": "1.0.0",
        "configuration": {"pooling_method": "cls"},
    }
    response = api_client.post(
        "/api/v1/meta/embeddings/models/test-vector-model-api/versions",
        json=version_payload,
    )
    assert response.status_code == 201
    assert response.json()["version_string"] == "1.0.0"

    # 3. Retrieve Active Model
    response = api_client.get("/api/v1/meta/embeddings/active")
    assert response.status_code == 200
    assert response.json()["id"] == "test-vector-model-api"

    # 4. Register a MetaType
    type_payload = {
        "id": "Aggregator",
        "name": "Data Aggregator Pattern",
        "category": "STRUCTURAL",
        "status": "EXPERIMENTAL",
    }
    response = api_client.post("/api/v1/meta/types", json=type_payload)
    assert response.status_code == 201
    assert response.json()["id"] == "Aggregator"
    assert response.json()["status"] == "EXPERIMENTAL"

    # 5. Register versioned schema definition
    schema_def = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "sources": {"type": "array"},
        },
        "required": ["id", "name"],
    }
    def_payload = {
        "schema_definition": schema_def,
        "semantic_signature": {"sources_min": 1},
        "version_string": "1.0.0",
    }
    response = api_client.post("/api/v1/meta/types/Aggregator/definitions", json=def_payload)
    assert response.status_code == 201
    assert response.json()["version_string"] == "1.0.0"

    # 6. Validate dynamic instance data
    # Case A: Valid instance
    response = api_client.post(
        "/api/v1/meta/types/Aggregator/validate",
        json={"id": "agg-1", "name": "PaymentAggregator", "sources": ["db", "api"]},
    )
    assert response.status_code == 200
    assert response.json()["valid"] is True

    # Case B: Invalid instance (missing required property 'name')
    response = api_client.post(
        "/api/v1/meta/types/Aggregator/validate",
        json={"id": "agg-2", "sources": []},
    )
    assert response.status_code == 422
    assert "detail" in response.json()

    # 7. Promotion Workflow
    # Case A: Promote EXPERIMENTAL -> CANDIDATE
    response = api_client.post("/api/v1/meta/types/Aggregator/request-candidate")
    assert response.status_code == 200
    assert "promoted" in response.json()["message"].lower()

    # Case B: Promote CANDIDATE -> ACTIVE
    approval_payload = {"approver": "Lead Architect"}
    response = api_client.post(
        "/api/v1/meta/types/Aggregator/approve-active",
        json=approval_payload,
    )
    assert response.status_code == 200
    assert "approved" in response.json()["message"].lower()

    # Case C: Deprecate type
    response = api_client.post("/api/v1/meta/types/Aggregator/deprecate")
    assert response.status_code == 200
    assert "deprecated" in response.json()["message"].lower()

    # 8. List Meta Types
    response = api_client.get("/api/v1/meta/types")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["id"] == "Aggregator"
    assert response.json()[0]["status"] == "DEPRECATED"


def test_meta_discovery_endpoint(api_client):
    # Retrieve container and database session
    container = api_client.app.state.container
    session = container.session_factory()
    uow = SQLAlchemyUnitOfWork(DummyEngine(session))

    repo_id = RepositoryId.generate()
    file_id = FileId.generate()
    location = CodeLocation(file_path="src/components.py", start_line=1, end_line=15, start_column=0, end_column=0)
    fingerprint = StructuralFingerprint(value="structural_fingerprint_value")

    # Seed Repo, SourceFile and similar CodeEntities in client DB context
    with uow:
        repo = RepositoryEntity(
            id=repo_id,
            url="https://github.com/test/repo-discovery",
            name="test-repo",
            default_branch="main",
            local_path="src/",
            status=AnalysisStatus.COMPLETED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        uow.repositories.save(repo)

        source_file = SourceFile(
            id=file_id,
            repository_id=repo_id,
            file_path="src/components.py",
            language=SupportedLanguage.PYTHON
        )
        uow.source_files.save(source_file)

        entity1 = CodeEntity(
            seid=SEID.generate(),
            entity_type=EntityType.CLASS,
            name="PageView",
            qualified_name="PageView",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=location,
            structural_fingerprint=fingerprint,
            metadata={"responsive": True},
        )
        entity2 = CodeEntity(
            seid=SEID.generate(),
            entity_type=EntityType.CLASS,
            name="WebView",
            qualified_name="WebView",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=location,
            structural_fingerprint=fingerprint,
            metadata={"responsive": True},
        )
        uow.code_entities.save(entity1)
        uow.code_entities.save(entity2)
        uow.commit()

    # 9. Trigger dynamic discovery run via REST API endpoint
    response = api_client.post(
        f"/api/v1/meta/discovery/run?repository_id={repo_id.value}&similarity_threshold=-1.0"
    )
    assert response.status_code == 200
    data = response.json()
    assert "candidates" in data
    assert len(data["candidates"]) > 0

    candidate = data["candidates"][0]
    assert candidate["meta_type"]["id"] == "View"
    assert candidate["meta_type"]["status"] == "EXPERIMENTAL"
    assert candidate["definition"]["schema_definition"]["title"] == "View"
    assert "responsive" in candidate["definition"]["schema_definition"]["properties"]
