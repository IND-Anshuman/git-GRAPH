"""Integration tests for Phase 4 concept REST API endpoints."""

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
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.entities.concept_relationship import ConceptRelationship
from src.domain.entities.concept_explanation import ConceptExplanation
from src.domain.entities.concept_drift import ConceptDrift
from src.domain.entities.concept_evolution import ConceptEvolution
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.enums.concept_relationship_type import ConceptRelationshipType
from src.domain.enums.concept_transition_type import ConceptTransitionType
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


def test_concepts_api_endpoints(api_client):
    container = api_client.app.state.container
    session = container.session_factory()
    uow = SQLAlchemyUnitOfWork(DummyEngine(session))

    repo_id = RepositoryId.generate()
    now = datetime.now(timezone.utc)

    concept_id = uuid.uuid4()
    ver_id = uuid.uuid4()
    expl_id = uuid.uuid4()

    # Seed test entities in database
    with uow:
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

        commit1 = Commit("hash1", repo_id, "Auth", "email", now, "C1", [])
        commit2 = Commit("hash2", repo_id, "Auth", "email", now, "C2", ["hash1"])
        uow.commits.save(commit1)
        uow.commits.save(commit2)

        # Update metadata for last analyzed commit
        repo.metadata["last_analyzed_commit"] = "hash2"
        uow.repositories.save(repo)

        c_node = ConceptNode(
            id=concept_id,
            repository_id=repo_id,
            ontology_node_id="security.authentication",
            name="Authentication",
            description="Auth module",
            is_system_defined=True,
            created_at=now,
            updated_at=now
        )
        uow.concept_nodes.save(c_node)

        c_ver = ConceptVersion(
            id=ver_id,
            concept_id=concept_id,
            commit_hash="hash2",
            version_number=1,
            confidence=0.94,
            is_active=True,
            metadata={},
            created_at=now
        )
        uow.concept_versions.save(c_ver)

        c_ev = ConceptEvidence(
            id=uuid.uuid4(),
            concept_version_id=ver_id,
            evidence_type="LOGIC_VERSION",
            target_id=uuid.uuid4(),
            confidence_contribution=0.90,
            metadata={},
            created_at=now
        )
        uow.concept_evidence.save_batch([c_ev])

        c_rel = ConceptRelationship(
            id=uuid.uuid4(),
            repository_id=repo_id,
            commit_hash="hash2",
            from_concept_id=concept_id,
            to_concept_id=concept_id,  # Self relationship for simple check
            relationship_type=ConceptRelationshipType.USES,
            confidence=0.85,
            metadata={},
            created_at=now
        )
        uow.concept_relationships.save(c_rel)

        c_expl = ConceptExplanation(
            id=expl_id,
            concept_version_id=ver_id,
            summary="Auth capability is verified",
            detail={"data": "test"},
            created_at=now
        )
        uow.concept_explanations.save(c_expl)

        c_drift = ConceptDrift(
            id=uuid.uuid4(),
            concept_id=concept_id,
            baseline_commit="hash1",
            current_commit="hash2",
            drift_score=0.15,
            drift_category="MINOR",
            dimension_scores={"structural": 0.15},
            computed_at=now
        )
        uow.concept_drift.save(c_drift)

        c_evo = ConceptEvolution(
            id=uuid.uuid4(),
            from_concept_version_id=None,
            to_concept_version_id=ver_id,
            transition_type=ConceptTransitionType.CONCEPT_CREATION,
            similarity_score=1.0,
            created_at=now
        )
        uow.concept_evolution.save(c_evo)

        uow.commit()

    # 1. GET /api/v1/repositories/{id}/concepts
    resp = api_client.get(f"/api/v1/repositories/{repo_id.value}/concepts")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Authentication"
    assert data[0]["confidence"] == 0.94

    # 2. GET /api/v1/concepts/{id}/timeline
    resp = api_client.get(f"/api/v1/concepts/{concept_id}/timeline")
    assert resp.status_code == 200
    timeline = resp.json()
    assert len(timeline) == 1
    assert timeline[0]["version_number"] == 1
    assert timeline[0]["transition"]["type"] == "CONCEPT_CREATION"

    # 3. GET /api/v1/concepts/{id}/drift
    resp = api_client.get(
        f"/api/v1/concepts/{concept_id}/drift",
        params={"baseline_commit": "hash1", "current_commit": "hash2"}
    )
    assert resp.status_code == 200
    drift_data = resp.json()
    assert drift_data["drift_score"] == 0.15
    assert drift_data["drift_category"] == "MINOR"

    # 4. GET /api/v1/repositories/{id}/concept-map
    resp = api_client.get(f"/api/v1/repositories/{repo_id.value}/concept-map")
    assert resp.status_code == 200
    cmap = resp.json()
    assert len(cmap["nodes"]) == 1
    assert cmap["nodes"][0]["label"] == "Authentication"

    # 5. GET /api/v1/concepts/version/{version_id}/explanation
    resp = api_client.get(f"/api/v1/concepts/version/{ver_id}/explanation")
    assert resp.status_code == 200
    expl_data = resp.json()
    assert "Auth capability" in expl_data["summary"]

    # 6. POST /api/v1/repositories/{id}/concepts/backfill
    # Since we mocked the backfill execution on mock repo, it should execute backfill_repository.
    # Triggering backfill on a repo with no structure or parser registered might throw or succeed
    # depending on mock setups. Let's see if it executes the endpoints correctly.
    resp = api_client.post(f"/api/v1/repositories/{repo_id.value}/concepts/backfill")
    # It should successfully execute backfill for the two commits seeded
    assert resp.status_code == 200
    backfill_data = resp.json()
    assert backfill_data["status"] == "success"
    assert backfill_data["processed_commits"] == 2
