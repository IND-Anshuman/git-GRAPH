"""Unit tests for Phase 4.75 Meta-Ontology, Schema Registry, Calibration, Governance, and Discovery services."""

import pytest
import uuid
from datetime import datetime
from sqlalchemy.orm import sessionmaker

from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.domain.entities.meta_ontology import MetaType, MetaDefinition, EmbeddingModel, EmbeddingVersion
from src.domain.entities.code_entity import CodeEntity
from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.domain.value_objects.fingerprint import StructuralFingerprint

from src.application.semantic.embedding.embedding_registry import EmbeddingRegistry
from src.application.semantic.calibration.calibration_engine import ConfidenceCalibrationEngine
from src.application.semantic.schema.schema_registry import SchemaRegistry
from src.application.semantic.governance.governance_manager import GovernanceManager
from src.application.semantic.discovery.entity_discovery_engine import EntityDiscoveryEngine


class DummyDatabaseEngine:
    def __init__(self, session_factory):
        self.session_factory = session_factory


@pytest.fixture
def uow(db_engine):
    session_factory = sessionmaker(bind=db_engine)
    db_mock = DummyDatabaseEngine(session_factory)
    return SQLAlchemyUnitOfWork(db_mock)


def test_embedding_registry(uow):
    """Test embedding model registration, configuration versions, and mock vectors."""
    registry = EmbeddingRegistry(uow)

    # 1. Register model
    model = registry.register_model(
        model_id="text-embedding-3-small",
        model_name="OpenAI Small Vector Model",
        provider="openai",
        dimensions=1536,
        distance_metric="cosine",
        is_active=False,
    )
    assert model.id == "text-embedding-3-small"
    assert not model.is_active

    # 2. Register version configuration
    version = registry.register_version(
        model_id="text-embedding-3-small",
        version_string="1.0.0",
        configuration={"pooling": "mean", "prefix": "query: "},
    )
    assert version.model_id == "text-embedding-3-small"
    assert version.version_string == "1.0.0"

    # 3. Activate model
    registry.activate_model("text-embedding-3-small")
    active = registry.get_active_model()
    assert active is not None
    assert active.id == "text-embedding-3-small"
    assert active.is_active

    # 4. Generate simulated vector
    vector = registry.generate_simulated_embedding("AuthService")
    assert len(vector) == 1536
    # Vector should be normalized
    assert pytest.approx(sum(x * x for x in vector), 1e-5) == 1.0


def test_confidence_calibration():
    """Test confidence engine functions: sigmoid scaling, Bayesian updates, and Noisy-OR aggregates."""
    engine = ConfidenceCalibrationEngine

    # 1. Sigmoidal scaling
    s1 = engine.sigmoidal_scale(0.0)
    s2 = engine.sigmoidal_scale(0.5)
    s3 = engine.sigmoidal_scale(1.0)
    assert s1 < s2 < s3

    # 2. Bayesian updates
    prior = 0.5
    updated_pos = engine.update_bayesian_prior(prior, likelihood_positive=0.8, likelihood_negative=0.2, observed=True)
    assert updated_pos > prior

    updated_neg = engine.update_bayesian_prior(prior, likelihood_positive=0.8, likelihood_negative=0.2, observed=False)
    assert updated_neg < prior

    # 3. Noisy-OR Aggregation
    agg_empty = engine.noisy_or_aggregate([])
    assert agg_empty == 0.0

    agg_values = engine.noisy_or_aggregate([0.6, 0.4])
    # 1 - ((1 - 0.6*1) * (1 - 0.4*0.5)) = 1 - (0.4 * 0.8) = 1 - 0.32 = 0.68
    assert pytest.approx(agg_values, 1e-5) == 0.68

    # 4. Taxonomic Decay Noisy-OR
    # (score, depth)
    evidence = [(0.8, 2), (0.7, 3)]
    agg_decay = engine.taxonomically_decayed_noisy_or(evidence, target_depth=1, base_decay=0.9)
    # distance to target_depth: |2 - 1| = 1, |3 - 1| = 2
    # effective_scores: 0.8 * 0.9 = 0.72; 0.7 * (0.9^2) = 0.7 * 0.81 = 0.567
    # Noisy-OR: 1 - (1 - 0.72) * (1 - 0.567) = 1 - (0.28 * 0.433) = 1 - 0.12124 = 0.87876
    assert pytest.approx(agg_decay, 1e-5) == 0.87876

    # 5. Joint Confidence calibration
    calib = engine.calibrate_joint_confidence([0.5, 0.4], max_single_score=0.5)
    # noisy_or is 1 - (1-0.5)*(1-0.2) = 0.6
    # cap is 0.5 + (1-0.5)*0.25 = 0.625
    # min(0.6, 0.625) = 0.6
    assert pytest.approx(calib, 1e-5) == 0.60


def test_schema_registry(uow):
    """Test schema type/definition registration and dynamic schema validation."""
    registry = SchemaRegistry(uow)

    # 1. Register MetaType
    meta_type = registry.register_type("Saga", "Saga Pattern Coordinator", "STRUCTURAL")
    assert meta_type.id == "Saga"
    assert meta_type.status == "EXPERIMENTAL"

    # 2. Register versioned schema definition
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "steps_count": {"type": "integer"},
        },
        "required": ["id", "name"],
    }
    meta_def = registry.register_definition(
        type_id="Saga",
        schema_definition=schema,
        semantic_signature={"has_state": True},
        version_string="1.0.0",
    )
    assert meta_def.type_id == "Saga"
    assert meta_def.version_string == "1.0.0"

    # 3. Validate correct instance
    valid, err = registry.validate_instance("Saga", {"id": "saga-1", "name": "PaymentSaga", "steps_count": 5})
    assert valid
    assert err is None

    # 4. Validate incorrect instance (missing required property)
    invalid, err_msg = registry.validate_instance("Saga", {"id": "saga-2", "steps_count": 2})
    assert not invalid
    assert "id" in err_msg or "name" in err_msg or "required" in err_msg.lower()


def test_governance_manager(uow):
    """Test promotion lifecycle states and threshold checks."""
    registry = SchemaRegistry(uow)
    gov = GovernanceManager(uow)

    # Setup type and schema definition
    registry.register_type("Component", "System Component", "STRUCTURAL")
    
    # 1. Cannot promote without a schema definition
    success, msg = gov.request_promotion_to_candidate("Component")
    assert not success
    assert "has no schema definitions" in msg

    # Register definitions
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
        },
    }
    registry.register_definition("Component", schema, {}, "1.0.0")

    # 2. Promotes successfully to CANDIDATE
    success, msg = gov.request_promotion_to_candidate("Component")
    assert success
    
    with uow:
        meta_type = uow.meta_types.get_by_id("Component")
        assert meta_type.status == "CANDIDATE"

    # 3. Cannot promote to ACTIVE without approver name
    success, msg = gov.approve_promotion_to_active("Component", "")
    assert not success

    # 4. Admin approves to ACTIVE
    success, msg = gov.approve_promotion_to_active("Component", "Security Committee")
    assert success
    
    with uow:
        meta_type = uow.meta_types.get_by_id("Component")
        assert meta_type.status == "ACTIVE"

    # 5. Deprecate type
    gov.deprecate_type("Component")
    with uow:
        meta_type = uow.meta_types.get_by_id("Component")
        assert meta_type.status == "DEPRECATED"


def test_entity_discovery_engine(uow):
    """Test EntityDiscoveryEngine groups similar entities and registers schema candidates."""
    emb_registry = EmbeddingRegistry(uow)
    schema_registry = SchemaRegistry(uow)
    calibration = ConfidenceCalibrationEngine()
    engine = EntityDiscoveryEngine(uow, emb_registry, schema_registry, calibration)

    repo_id = RepositoryId.generate()
    file_id = FileId.generate()
    location = CodeLocation(file_path="src/services.py", start_line=1, end_line=20, start_column=0, end_column=0)
    fingerprint = StructuralFingerprint(value="mock_fingerprint_hash_value")

    # Seed similar code entities in the repo (with the same suffix 'Service')
    from src.domain.entities.repository import RepositoryEntity
    from src.domain.entities.source_file import SourceFile
    from src.domain.enums.analysis_status import AnalysisStatus

    with uow:
        # Seed Repo
        repo = RepositoryEntity(
            id=repo_id,
            url="https://github.com/test/repo",
            name="test-repo",
            default_branch="main",
            local_path="src/",
            status=AnalysisStatus.COMPLETED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        uow.repositories.save(repo)

        # Seed SourceFile
        source_file = SourceFile(
            id=file_id,
            repository_id=repo_id,
            file_path="src/services.py",
            language=SupportedLanguage.PYTHON
        )
        uow.source_files.save(source_file)

        entity1 = CodeEntity(
            seid=SEID.generate(),
            entity_type=EntityType.CLASS,
            name="AppService",
            qualified_name="AppService",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=location,
            structural_fingerprint=fingerprint,
            metadata={"async": True, "database_access": True},
        )
        entity2 = CodeEntity(
            seid=SEID.generate(),
            entity_type=EntityType.CLASS,
            name="AuthService",
            qualified_name="AuthService",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=location,
            structural_fingerprint=fingerprint,
            metadata={"async": True, "database_access": True},
        )

        uow.code_entities.save(entity1)
        uow.code_entities.save(entity2)
        uow.commit()

    # Lower similarity threshold to -1.0 to ensure clustering succeeds despite pseudo-random mock vectors
    candidates = engine.discover_semantic_types(repo_id, similarity_threshold=-1.0)

    assert len(candidates) > 0
    candidate_type, candidate_def = candidates[0]
    
    assert candidate_type.id == "Service"
    assert candidate_type.name == "Service"
    assert candidate_type.status == "EXPERIMENTAL"
    
    schema = candidate_def.schema_definition
    assert schema["title"] == "Service"
    assert "async" in schema["properties"]
    assert "database_access" in schema["properties"]
    assert "$confidence" in schema
