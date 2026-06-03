"""Integration tests for the temporal explorer and replay API endpoints."""

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
from src.domain.entities.relationship import Relationship
from src.domain.entities.relationship_version import RelationshipVersion
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.enums.mutation_type import MutationType
from src.domain.enums.entity_type import EntityType
from src.domain.enums.relationship_type import RelationshipType
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

def test_explorer_and_replay_endpoints(api_client):
    container = api_client.app.state.container
    uow_factory = container.get_uow_factory()

    repo_id = RepositoryId.generate()
    repo_uuid_str = str(repo_id.value)
    
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
        
        # Commits (hash1 -> hash2)
        commit1 = Commit("hash1", repo_id, "Auth", "email", now - datetime.timedelta(minutes=10), "C1", [])
        commit2 = Commit("hash2", repo_id, "Auth", "email", now, "C2", ["hash1"])
        uow.commits.save(commit1)
        uow.commits.save(commit2)
        
        # Entity
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
        
        # Entity Versions
        ev1 = EntityVersion(
            id=uuid.uuid4(),
            seid=valid_seid,
            commit_hash="hash1",
            version_ordinal=1,
            mutation_type=MutationType.CREATED,
            canonical_name="func",
            file_path="src/file.py",
            start_line=1,
            end_line=5,
            content_hash="h1",
            structural_fingerprint="fp1"
        )
        ev2 = EntityVersion(
            id=uuid.uuid4(),
            seid=valid_seid,
            commit_hash="hash2",
            version_ordinal=2,
            mutation_type=MutationType.MODIFIED,
            canonical_name="func",
            file_path="src/file.py",
            start_line=1,
            end_line=7,
            content_hash="h2",
            structural_fingerprint="fp1"
        )
        uow.entity_versions.save(ev1)
        uow.entity_versions.save(ev2)

        # Relationship
        rel_uuid = uuid.uuid4()
        rel = Relationship(
            id=rel_uuid,
            repository_id=repo_id,
            relationship_type=RelationshipType.CALLS,
            source_seid=valid_seid,
            target_seid=valid_seid
        )
        uow.relationships.save(rel)

        # Relationship Version
        rv = RelationshipVersion(
            id=uuid.uuid4(),
            relationship_id=rel_uuid,
            commit_hash="hash1",
            mutation_type=MutationType.CREATED,
            version_ordinal=1
        )
        uow.relationship_versions.save(rv)
        
        uow.commit()

    # 1. Test Entity Explorer endpoint
    response = api_client.get(f"/api/v1/repositories/{repo_uuid_str}/explorer/entity/{str(valid_seid)}/evolution")
    assert response.status_code == 200
    versions = response.json()
    assert len(versions) == 2
    assert versions[0]["version_ordinal"] == 1
    assert versions[0]["commit_hash"] == "hash1"
    assert versions[1]["version_ordinal"] == 2
    assert versions[1]["commit_hash"] == "hash2"

    # 2. Test Relationship Explorer endpoint
    response = api_client.get(f"/api/v1/repositories/{repo_uuid_str}/explorer/relationship/{str(rel_uuid)}/evolution")
    assert response.status_code == 200
    timeline = response.json()
    assert len(timeline) == 1
    assert timeline[0]["commit_hash"] == "hash1"
    assert timeline[0]["mutation_type"] == "CREATED"

    # 3. Test Replay endpoint
    response = api_client.get(f"/api/v1/repositories/{repo_uuid_str}/replay?start_commit=hash1&end_commit=hash2")
    assert response.status_code == 200
    steps = response.json()
    assert len(steps) == 2
    
    # Check step 1 (hash1) deltas
    assert steps[0]["commit_hash"] == "hash1"
    assert len(steps[0]["delta"]["added_nodes"]) == 1
    assert steps[0]["delta"]["added_nodes"][0]["seid"] == str(valid_seid)

    # Check step 2 (hash2) deltas
    assert steps[1]["commit_hash"] == "hash2"
    assert len(steps[1]["delta"]["modified_nodes"]) == 1
    assert steps[1]["delta"]["modified_nodes"][0]["seid"] == str(valid_seid)
    
    # Check visualization graph output contains nodes and links
    assert "nodes" in steps[1]["graph"]
    assert "links" in steps[1]["graph"]
