"""Unit tests for Phase 4 concept detection engine and ontology registry."""

import uuid
from datetime import datetime, timezone
import pytest
import yaml

from src.domain.entities.repository import RepositoryEntity
from src.domain.entities.commit import Commit
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.logic_signature import LogicSignature
from src.domain.entities.logic_version import LogicVersion
from src.domain.entities.logic_evidence import LogicEvidence
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.domain.enums.evidence_type import EvidenceType
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.logic_fingerprint import LogicFingerprint
from src.domain.value_objects.code_location import CodeLocation
from src.domain.exceptions import OntologyLoadException, ConceptDomainException
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.application.services.ontology_registry import ConceptOntologyRegistry
from src.application.services.concept_detection_engine import ConceptDetectionEngine


class DummyEngine:
    def __init__(self, session):
        self.session_factory = lambda: session


def test_ontology_registry_cycle_detection(tmp_path):
    # Create invalid ontology YAML containing a parent-child cycle
    cycle_yaml = tmp_path / "concepts_cycle.yaml"
    cycle_yaml.write_text("""
schema_version: "4.0"
domains:
  - id: security
    name: Security
    concepts:
      - id: security.authentication
        name: Authentication
        parent_id: security.authorization
        required_patterns: []
      - id: security.authorization
        name: Authorization
        parent_id: security.authentication
        required_patterns: []
""", encoding="utf-8")

    with pytest.raises(OntologyLoadException) as exc_info:
        ConceptOntologyRegistry(yaml_path=str(cycle_yaml))

    assert "cycle detected" in str(exc_info.value).lower()


def test_concept_classification_and_calibration(db_session, tmp_path):
    # Setup temp valid concepts.yaml
    valid_yaml = tmp_path / "concepts.yaml"
    valid_yaml.write_text("""
schema_version: "4.0"
domains:
  - id: security
    name: Security
    concepts:
      - id: security.authentication
        name: Authentication
        required_patterns:
          - auth_bcrypt_verification
        optional_patterns:
          - auth_direct_compare
        min_base_confidence: 0.75
""", encoding="utf-8")

    registry = ConceptOntologyRegistry(yaml_path=str(valid_yaml))
    engine = ConceptDetectionEngine(ontology_registry=registry)

    # 1. Setup seed database logic records
    uow = SQLAlchemyUnitOfWork(DummyEngine(db_session))
    repo_id = RepositoryId.generate()
    now = datetime.now(timezone.utc)

    with uow:
        # Save repo and commit
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

        commit = Commit("hash123", repo_id, "Author", "email", now, "Commit 1", [])
        uow.commits.save(commit)

        # Save code entity
        seid = SEID.generate()
        entity = CodeEntity(
            seid=seid,
            entity_type=EntityType.FUNCTION,
            name="login",
            qualified_name="login",
            file_id=FileId(uuid.uuid4()),
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=CodeLocation("src/auth.py", 1, 10, 0, 0)
        )
        uow.code_entities.save(entity)

        # Save logic signature with ontology_node_id
        sig = LogicSignature(
            id=uuid.uuid4(),
            repository_id=repo_id,
            canonical_name="auth_bcrypt_verification",
            language=SupportedLanguage.PYTHON,
            ontology_node_id="security.authentication.hash_comparison",
            description="bcrypt password validation pattern",
            created_at=now
        )
        uow.logic_signatures.save(sig)

        # Save logic version
        l_ver = LogicVersion(
            id=uuid.uuid4(),
            logic_signature_id=sig.id,
            code_entity_seid=seid,
            commit_hash="hash123",
            version_ordinal=1,
            fingerprint=LogicFingerprint("a", "b", "c", "abc"),
            overall_confidence=0.80,
            is_primary=True,
            created_at=now
        )
        uow.logic_versions.save(l_ver)

        # Save logic evidence
        ev = LogicEvidence(
            id=uuid.uuid4(),
            logic_version_id=l_ver.id,
            evidence_type=EvidenceType.AST_CALL,
            file_path="src/auth.py",
            start_line=1,
            end_line=10,
            matched_symbol="bcrypt.checkpw",
            confidence_contribution=0.80,
            detected_at=now
        )
        # In this codebase, the confidence property name is 'confidence_contribution'
        # but let's check: in the database, is it mapped? Let's check logic_evidence property.
        # Yes, we saw it is logic_evidence.py: confidence_contribution
        uow.logic_evidence.save_batch([ev])

        uow.commit()

    # 2. Run detection and assert
    with uow:
        results = engine.detect_concepts(uow, repo_id, "hash123")
        assert len(results) == 1
        node, ver, evidences = results[0]

        assert node.ontology_node_id == "security.authentication"
        assert node.name == "Authentication"
        
        # Test calibration step-down decay and clamp bounds
        # Joint confidence with single item 0.80 should calibrate above 0.80 but within bounds
        assert ver.confidence >= 0.80
        assert ver.confidence <= 1.00

        # Verify correct evidence links
        assert len(evidences) >= 1
        assert any(e.evidence_type == "LOGIC_VERSION" for e in evidences)


def test_concept_explosion_safeguard(db_session, tmp_path):
    # Setup temporary valid concepts.yaml with multiple concepts
    valid_yaml = tmp_path / "concepts_explosion.yaml"
    valid_yaml.write_text("""
schema_version: "4.0"
domains:
  - id: security
    name: Security
    concepts:
      - id: security.authentication
        name: Authentication
        required_patterns:
          - auth_bcrypt_verification
        min_base_confidence: 0.10
""", encoding="utf-8")

    registry = ConceptOntologyRegistry(yaml_path=str(valid_yaml))
    engine = ConceptDetectionEngine(ontology_registry=registry)
    # Set limit to a low number (e.g. 0) to trigger concept explosion exception
    engine.MAX_CONCEPTS_PER_COMMIT = 0

    uow = SQLAlchemyUnitOfWork(DummyEngine(db_session))
    repo_id = RepositoryId.generate()
    now = datetime.now(timezone.utc)

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

        commit = Commit("hash123", repo_id, "Author", "email", now, "C1", [])
        uow.commits.save(commit)

        seid = SEID.generate()
        entity = CodeEntity(
            seid=seid,
            entity_type=EntityType.FUNCTION,
            name="login",
            qualified_name="login",
            file_id=FileId(uuid.uuid4()),
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=CodeLocation("src/auth.py", 1, 10, 0, 0)
        )
        uow.code_entities.save(entity)

        sig = LogicSignature(
            id=uuid.uuid4(),
            repository_id=repo_id,
            canonical_name="auth_bcrypt_verification",
            language=SupportedLanguage.PYTHON,
            ontology_node_id="security.authentication.hash_comparison",
            description="bcrypt password validation pattern",
            created_at=now
        )
        uow.logic_signatures.save(sig)

        l_ver = LogicVersion(
            id=uuid.uuid4(),
            logic_signature_id=sig.id,
            code_entity_seid=seid,
            commit_hash="hash123",
            version_ordinal=1,
            fingerprint=LogicFingerprint("a", "b", "c", "abc"),
            overall_confidence=0.80,
            is_primary=True,
            created_at=now
        )
        uow.logic_versions.save(l_ver)
        uow.commit()

    with uow:
        with pytest.raises(ConceptDomainException) as exc_info:
            engine.detect_concepts(uow, repo_id, "hash123")
        assert "concept explosion" in str(exc_info.value).lower()
