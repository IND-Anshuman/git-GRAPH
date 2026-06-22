"""Integration tests for Phase 3 logic REST API endpoints."""

import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from src.config import settings
from src.main import app
from src.infrastructure.persistence.models import Base
from src.domain.entities.repository import RepositoryEntity
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.logic_signature import LogicSignature
from src.domain.entities.logic_version import LogicVersion
from src.domain.entities.logic_evidence import LogicEvidence
from src.domain.entities.logic_transition import LogicTransition
from src.domain.entities.behavior_explanation import BehaviorExplanation, RuleVerdict
from src.domain.entities.behavior_drift import BehaviorDrift
from src.domain.entities.ontology_node import OntologyNode
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.domain.enums.evidence_type import EvidenceType
from src.domain.enums.transition_type import TransitionType
from src.domain.enums.drift_category import DriftCategory
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.domain.value_objects.logic_fingerprint import LogicFingerprint
from src.domain.value_objects.confidence_breakdown import ConfidenceBreakdown
from src.domain.value_objects.drift_dimensions import DriftDimensions
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


def test_logic_api_endpoints(api_client):
    # Retrieve the container and session
    container = api_client.app.state.container
    session = container.session_factory()
    uow = SQLAlchemyUnitOfWork(DummyEngine(session))
    
    repo_id = RepositoryId.generate()
    now = datetime.now(timezone.utc)
    
    # Setup test data
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
        
        seid1 = SEID.generate()
        entity = CodeEntity(
            seid=seid1,
            entity_type=EntityType.FUNCTION,
            name="test_func",
            qualified_name="test_func",
            file_id=FileId(uuid.uuid4()),
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=CodeLocation("src/test.py", 1, 10, 0, 0)
        )
        uow.code_entities.save(entity)
        
        onto_node = OntologyNode(
            id="security.authentication.hash_comparison",
            name="Cryptographic Hash Verification",
            parent_id=None,
            domain="Security",
            description="Verification via hashing",
            ontology_version="3.0.0"
        )
        uow.ontology_nodes.save(onto_node)

        sig_id = uuid.uuid4()
        sig = LogicSignature(
            id=sig_id,
            repository_id=repo_id,
            canonical_name="auth_bcrypt_verification",
            language=SupportedLanguage.PYTHON,
            ontology_node_id="security.authentication.hash_comparison",
            description="bcrypt verification",
            created_at=now,
            metadata={}
        )
        uow.logic_signatures.save(sig)
        
        ver_id = uuid.uuid4()
        fp = LogicFingerprint.compute("s1", "d1", "b1")
        cb = ConfidenceBreakdown.compute(0.95, 0.95, 0.95, 0.95, 0.95, 1)
        ver = LogicVersion(
            id=ver_id,
            logic_signature_id=sig_id,
            code_entity_seid=seid1,
            commit_hash="hash1",
            version_ordinal=1,
            fingerprint=fp,
            overall_confidence=0.95,
            confidence_breakdown=cb,
            is_primary=True,
            metadata={"source_file": "src/test.py", "entity_seid": str(seid1)},
            created_at=now
        )
        uow.logic_versions.save(ver)
        
        evid = LogicEvidence(
            id=uuid.uuid4(),
            logic_version_id=ver_id,
            evidence_type=EvidenceType.AST_CALL,
            file_path="src/test.py",
            start_line=5,
            end_line=5,
            ast_node_type="Call",
            matched_symbol="bcrypt.checkpw",
            matched_rule_id="r1",
            confidence_contribution=0.50,
            metadata={},
            detected_at=now
        )
        uow.logic_evidence.save_batch([evid])
        
        expl = BehaviorExplanation(
            id=uuid.uuid4(),
            logic_version_id=ver_id,
            behavior_name="Bcrypt Verification",
            ontology_path="security.authentication.hash_comparison",
            overall_confidence=0.95,
            confidence_breakdown=cb,
            matched_pattern_ids=["auth_bcrypt_verification"],
            evidence_summary="Matched bcrypt",
            rule_verdicts=[
                RuleVerdict(rule_id="r1", rule_description="bcrypt call", passed=True, contribution=0.50, evidence_ref=evid.id)
            ],
            is_stale=False,
            generated_at=now,
            metadata={"behavior_name": "Bcrypt Verification", "ontology_path": "security.authentication.hash_comparison", "confidence_breakdown": cb.to_dict(), "matched_pattern_ids": ["auth_bcrypt_verification"]}
        )
        uow.behavior_explanations.save(expl)
        
        uow.commit()
    
    # 1. Test get_entity_logic endpoint
    response = api_client.get(f"/api/v1/logic/entity/{seid1}?commit_hash=hash1")
    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data) == 1
    assert res_data[0]["id"] == str(ver_id)
    assert res_data[0]["logic_signature_id"] == str(sig_id)
    assert res_data[0]["overall_confidence"] == 0.95

    # 2. Test get_entity_logic_history endpoint
    response = api_client.get(f"/api/v1/logic/entity/{seid1}/history")
    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data) == 1
    assert res_data[0]["id"] == str(ver_id)

    # 3. Test get_behavior_evolution endpoint
    response = api_client.get(f"/api/v1/logic/signature/{sig_id}/evolution")
    assert response.status_code == 200
    res_data = response.json()
    assert "versions" in res_data
    assert len(res_data["versions"]) == 1
    assert res_data["versions"][0]["id"] == str(ver_id)

    # 4. Test get_logic_evidence endpoint
    response = api_client.get(f"/api/v1/logic/version/{ver_id}/evidence")
    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data) == 1
    assert res_data[0]["matched_symbol"] == "bcrypt.checkpw"

    # 5. Test get_behavior_explanation endpoint
    response = api_client.get(f"/api/v1/logic/version/{ver_id}/explanation")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["behavior_name"] == "Bcrypt Verification"
    assert res_data["evidence_summary"] == "Matched bcrypt"
    assert len(res_data["rule_verdicts"]) == 1
    assert res_data["rule_verdicts"][0]["rule_description"] == "bcrypt call"

    # 6. Test validate_logic endpoint (should succeed/run validation checks)
    response = api_client.get("/api/v1/logic/validate")
    assert response.status_code == 200
    res_data = response.json()
    assert "is_valid" in res_data
    assert "issues" in res_data


def test_new_logic_endpoints(api_client):
    # Retrieve the container and session
    container = api_client.app.state.container
    session = container.session_factory()
    uow = SQLAlchemyUnitOfWork(DummyEngine(session))
    
    repo_id = RepositoryId.generate()
    now = datetime.now(timezone.utc)
    
    # Setup test data
    with uow:
        repo = RepositoryEntity(
            id=repo_id,
            url="https://github.com/test/repo2",
            name="test-repo2",
            default_branch="main",
            local_path="src/",
            status=AnalysisStatus.COMPLETED,
            created_at=now,
            updated_at=now
        )
        uow.repositories.save(repo)
        
        seid1 = SEID.generate()
        entity = CodeEntity(
            seid=seid1,
            entity_type=EntityType.FUNCTION,
            name="test_func",
            qualified_name="test_func",
            file_id=FileId(uuid.uuid4()),
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=CodeLocation("src/test.py", 1, 10, 0, 0)
        )
        uow.code_entities.save(entity)
        
        onto_node = OntologyNode(
            id="security.authentication.hash_comparison",
            name="Cryptographic Hash Verification",
            parent_id=None,
            domain="Security",
            description="Verification via hashing",
            ontology_version="3.0.0"
        )
        uow.ontology_nodes.save(onto_node)

        sig_id = uuid.uuid4()
        sig = LogicSignature(
            id=sig_id,
            repository_id=repo_id,
            canonical_name="auth_bcrypt_verification",
            language=SupportedLanguage.PYTHON,
            ontology_node_id="security.authentication.hash_comparison",
            description="bcrypt verification",
            created_at=now,
            metadata={"entity_seid": str(seid1.value), "entity_name": "test_func", "entity_type": "FUNCTION", "file_path": "src/test.py", "overall_confidence": 0.95}
        )
        uow.logic_signatures.save(sig)
        
        ver_id = uuid.uuid4()
        fp = LogicFingerprint.compute("s1", "d1", "b1")
        cb = ConfidenceBreakdown.compute(0.95, 0.95, 0.95, 0.95, 0.95, 1)
        ver = LogicVersion(
            id=ver_id,
            logic_signature_id=sig_id,
            code_entity_seid=seid1,
            commit_hash="hash1",
            version_ordinal=1,
            fingerprint=fp,
            overall_confidence=0.95,
            confidence_breakdown=cb,
            is_primary=True,
            metadata={"source_file": "src/test.py", "entity_seid": str(seid1)},
            created_at=now
        )
        uow.logic_versions.save(ver)
        
        evid = LogicEvidence(
            id=uuid.uuid4(),
            logic_version_id=ver_id,
            evidence_type=EvidenceType.AST_CALL,
            file_path="src/test.py",
            start_line=5,
            end_line=5,
            ast_node_type="Call",
            matched_symbol="bcrypt.checkpw",
            matched_rule_id="r1",
            confidence_contribution=0.50,
            metadata={},
            detected_at=now
        )
        uow.logic_evidence.save_batch([evid])
        
        expl = BehaviorExplanation(
            id=uuid.uuid4(),
            logic_version_id=ver_id,
            behavior_name="Bcrypt Verification",
            ontology_path="security.authentication.hash_comparison",
            overall_confidence=0.95,
            confidence_breakdown=cb,
            matched_pattern_ids=["auth_bcrypt_verification"],
            evidence_summary="Matched bcrypt",
            rule_verdicts=[
                RuleVerdict(rule_id="r1", rule_description="bcrypt call", passed=True, contribution=0.50, evidence_ref=evid.id)
            ],
            is_stale=False,
            generated_at=now,
            metadata={"behavior_name": "Bcrypt Verification", "ontology_path": "security.authentication.hash_comparison", "confidence_breakdown": cb.to_dict(), "matched_pattern_ids": ["auth_bcrypt_verification"]}
        )
        uow.behavior_explanations.save(expl)
        
        uow.commit()

    # 1. Test Repository Logic Timeline Query
    response = api_client.get(f"/api/v1/logic/repositories/{repo_id}/timeline")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["repository_id"] == str(repo_id.value)
    assert len(res_data["signatures"]) == 1
    sig_timeline = res_data["signatures"][0]
    assert sig_timeline["signature"]["id"] == str(sig_id)
    assert len(sig_timeline["versions"]) == 1
    assert sig_timeline["versions"][0]["id"] == str(ver_id)
    assert len(sig_timeline["evidence"]) == 1
    assert sig_timeline["evidence"][0]["matched_symbol"] == "bcrypt.checkpw"

    # 2. Test Repository Bulk Extraction (Trigger Endpoint)
    response = api_client.post(f"/api/v1/logic/repositories/{repo_id}/extract-all")
    assert response.status_code == 202
    assert response.json()["status"] == "success"
