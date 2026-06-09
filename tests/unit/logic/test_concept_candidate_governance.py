"""Unit tests for concept candidate discovery and governance promotion."""

import pytest
import uuid
from datetime import datetime
from sqlalchemy.orm import sessionmaker

from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.entity_id import SEID
from src.domain.enums.language import SupportedLanguage
from src.domain.entities.logic_signature import LogicSignature
from src.domain.entities.ontology_node import OntologyNode
from src.application.semantic.embedding.embedding_registry import EmbeddingRegistry
from src.application.semantic.calibration.calibration_engine import ConfidenceCalibrationEngine
from src.application.semantic.schema.schema_registry import SchemaRegistry
from src.application.semantic.governance.governance_manager import GovernanceManager
from src.application.semantic.discovery.concept_discovery_engine import ConceptDiscoveryEngine


class DummyDatabaseEngine:
    def __init__(self, session_factory):
        self.session_factory = session_factory


@pytest.fixture
def uow(db_engine):
    session_factory = sessionmaker(bind=db_engine)
    db_mock = DummyDatabaseEngine(session_factory)
    return SQLAlchemyUnitOfWork(db_mock)


def test_concept_discovery_and_promotion(uow):
    """Test co-occurrence discovery of concept candidates and their governance promotion to ConceptNode."""
    emb_registry = EmbeddingRegistry(uow)
    schema_registry = SchemaRegistry(uow)
    calibration = ConfidenceCalibrationEngine()
    
    # Instantiate the engines
    discovery_engine = ConceptDiscoveryEngine(
        uow=uow,
        schema_registry=schema_registry,
        embedding_registry=emb_registry,
        calibration_engine=calibration
    )
    gov_manager = GovernanceManager(uow)

    repo_id = RepositoryId.generate()
    
    # 1. Seed the ontology node to place candidate under
    ontology_node = OntologyNode(
        id="security.authentication",
        name="Authentication",
        parent_id=None,
        domain="Security",
        description="Verify identity",
        ontology_version="1.0.0",
        is_leaf=True,
        metadata={},
        loaded_at=datetime.utcnow()
    )

    with uow:
        # Seed Repo/SourceFile not strictly required since we only query signatures for co-occurrence,
        # but let's seed ontology nodes.
        uow.ontology_nodes.save(ontology_node)
        
        # Seed 2 co-occurring logic signatures that share a file
        sig1 = LogicSignature(
            id=uuid.uuid4(),
            repository_id=repo_id,
            canonical_name="jwt_authenticate",
            language=SupportedLanguage.PYTHON,
            ontology_node_id="security.authentication",
            description="authenticates via JWT token",
            created_at=datetime.utcnow(),
            metadata={
                "entity_seid": str(uuid.uuid4()),
                "entity_name": "jwt_auth_func",
                "entity_type": "FUNCTION",
                "file_path": "src/security/auth.py",
                "overall_confidence": 0.95
            }
        )
        sig2 = LogicSignature(
            id=uuid.uuid4(),
            repository_id=repo_id,
            canonical_name="oauth_authenticate",
            language=SupportedLanguage.PYTHON,
            ontology_node_id="security.authentication",
            description="authenticates via OAuth Provider",
            created_at=datetime.utcnow(),
            metadata={
                "entity_seid": str(uuid.uuid4()),
                "entity_name": "oauth_auth_func",
                "entity_type": "FUNCTION",
                "file_path": "src/security/auth.py",
                "overall_confidence": 0.90
            }
        )

        uow.logic_signatures.save(sig1)
        uow.logic_signatures.save(sig2)
        uow.commit()

    # 2. Discover concept candidates
    candidates = discovery_engine.discover_concept_candidates(
        repository_id=repo_id,
        similarity_threshold=0.50
    )

    assert len(candidates) == 1
    cand = candidates[0]
    assert "auth" in cand.name.lower() or "discovered" in cand.name.lower()
    assert cand.status == "CANDIDATE"
    assert cand.ontology_parent_candidate == "security.authentication"
    assert len(cand.evidence.supporting_entities) == 2
    assert len(cand.evidence.supporting_behaviors) == 2

    # Check that it's staged as a CANDIDATE MetaType in the database
    with uow:
        meta_type = uow.meta_types.get_by_id(str(cand.id))
        assert meta_type is not None
        assert meta_type.status == "CANDIDATE"
        assert meta_type.category == "CONCEPTUAL"

    # 3. Approve and Promote Concept Candidate
    success, msg = gov_manager.approve_promotion_to_active(
        type_id=str(cand.id),
        approver_name="AdminUser"
    )
    assert success
    assert "approved as APPROVED" in msg

    # 4. Verify ConceptNode creation and status update
    with uow:
        meta_type = uow.meta_types.get_by_id(str(cand.id))
        assert meta_type.status == "APPROVED"

        concept_node = uow.concept_nodes.get_by_id(cand.id)
        assert concept_node is not None
        assert concept_node.repository_id == repo_id
        assert concept_node.ontology_node_id == "security.authentication"
        assert concept_node.name == meta_type.name
        assert not concept_node.is_system_defined
