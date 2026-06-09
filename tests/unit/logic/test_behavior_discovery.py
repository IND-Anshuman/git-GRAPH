"""Unit tests for BehaviorDiscoveryEngine and CompositeBehaviorFingerprint similarity clustering."""

import pytest
import uuid
from sqlalchemy.orm import sessionmaker

from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.composite_fingerprint import CompositeBehaviorFingerprint
from src.application.semantic.calibration.calibration_engine import ConfidenceCalibrationEngine
from src.application.semantic.schema.schema_registry import SchemaRegistry
from src.application.semantic.discovery.behavior_discovery_engine import BehaviorDiscoveryEngine
from src.application.semantic.isr.canonical_entity import CanonicalEntity


class DummyDatabaseEngine:
    def __init__(self, session_factory):
        self.session_factory = session_factory


@pytest.fixture
def uow(db_engine):
    session_factory = sessionmaker(bind=db_engine)
    db_mock = DummyDatabaseEngine(session_factory)
    return SQLAlchemyUnitOfWork(db_mock)


def test_composite_behavior_fingerprint_similarity():
    """Verify the weighted Jaccard calculation of CompositeBehaviorFingerprint."""
    # Weight configuration:
    # 0.25*AST + 0.25*Calls + 0.15*Imports + 0.20*DataFlow + 0.15*Tokens

    # Case 1: Identical fingerprints should have 1.0 similarity
    fp1 = CompositeBehaviorFingerprint(
        ast_shape="func, var, call",
        call_signature="bcrypt.checkpw, hash",
        import_signature="bcrypt",
        data_flow_signature="input_pw -> checkpw",
        semantic_tokens="auth verify password",
    )
    assert pytest.approx(fp1.calculate_similarity(fp1), 1e-5) == 1.0

    # Case 2: Divergent fingerprints
    fp2 = CompositeBehaviorFingerprint(
        ast_shape="func, var, call",       # 1.0 similarity (AST weight = 0.25) -> 0.25
        call_signature="hashlib.sha256",    # 0.0 similarity (Calls weight = 0.25) -> 0.0
        import_signature="hashlib",         # 0.0 similarity (Imports weight = 0.15) -> 0.0
        data_flow_signature="input_pw -> checkpw", # 1.0 similarity (DataFlow weight = 0.20) -> 0.20
        semantic_tokens="crypto hashing",   # 0.0 similarity (Tokens weight = 0.15) -> 0.0
    )
    # Expected: 0.25*1.0 + 0.25*0.0 + 0.15*0.0 + 0.20*1.0 + 0.15*0.0 = 0.45
    assert pytest.approx(fp1.calculate_similarity(fp2), 1e-5) == 0.45


def test_behavior_discovery_clustering_and_registration(uow):
    """Test clustering identical or highly similar method behaviors into experimental MetaTypes."""
    schema_registry = SchemaRegistry(uow)
    calibration = ConfidenceCalibrationEngine()
    engine = BehaviorDiscoveryEngine(uow, schema_registry, calibration)
    repo_id = RepositoryId.generate()

    # 1. Define highly similar methods (Saga coordinators)
    saga_method_1 = CanonicalEntity(
        id=str(uuid.uuid4()),
        name="execute_payment_saga",
        qualified_name="execute_payment_saga",
        entity_type="Method",
        metadata={
            "ast_shape": "func, block, try, except, call",
            "calls": ["saga.step", "saga.compensate", "db.save"],
            "imports": ["saga_orchestrator"],
            "data_flow": ["context -> step -> compensate"],
            "semantic_tokens": ["orchestration", "transaction", "saga"],
        },
    )

    saga_method_2 = CanonicalEntity(
        id=str(uuid.uuid4()),
        name="execute_shipment_saga",
        qualified_name="execute_shipment_saga",
        entity_type="Method",
        metadata={
            "ast_shape": "func, block, try, except, call",
            "calls": ["saga.step", "saga.compensate", "logging.info"], # slightly different call
            "imports": ["saga_orchestrator"],
            "data_flow": ["context -> step -> compensate"],
            "semantic_tokens": ["orchestration", "transaction", "saga"],
        },
    )

    # 2. Define a divergent method (e.g. hashing)
    hash_method = CanonicalEntity(
        id=str(uuid.uuid4()),
        name="hash_password",
        qualified_name="hash_password",
        entity_type="Method",
        metadata={
            "ast_shape": "func, return",
            "calls": ["hashlib.pbkdf2_hmac"],
            "imports": ["hashlib"],
            "data_flow": ["password -> pbkdf2_hmac -> return"],
            "semantic_tokens": ["crypto", "security"],
        },
    )

    entities = [saga_method_1, saga_method_2, hash_method]

    # Run discovery with 0.70 threshold. saga_method_1 and saga_method_2 should cluster together.
    # similarity:
    # AST: 1.0 (0.25)
    # Calls: saga.step, saga.compensate common -> intersection: 2, union: 4 -> 0.5 (0.125)
    # Imports: 1.0 (0.15)
    # DataFlow: 1.0 (0.20)
    # Tokens: 1.0 (0.15)
    # Total: 0.25 + 0.125 + 0.15 + 0.20 + 0.15 = 0.875 >= 0.70
    candidates = engine.discover_behavior_clusters(
        repository_id=repo_id,
        entities=entities,
        similarity_threshold=0.70,
    )

    # We expect the two Saga methods to be clustered together into one behavioral MetaType,
    # and the singleton hash_method to fallback into its own cluster.
    assert len(candidates) >= 1

    # Find the Saga cluster (which contains saga_method_1 and saga_method_2)
    saga_candidate = next((c for c in candidates if "saga" in c[0].name.lower() or "execute" in c[0].name.lower()), None)
    assert saga_candidate is not None

    meta_type, meta_def = saga_candidate
    assert meta_type.category == "BEHAVIORAL"
    assert meta_type.status == "EXPERIMENTAL"
    
    # Verify definition schema and semantic signature
    assert meta_def.schema_definition["title"] == meta_type.name
    assert meta_def.semantic_signature["entity_count"] == 2
    assert meta_def.schema_definition["$confidence"] > 0.5
    assert saga_method_1.name in meta_def.semantic_signature["aliases"]
    assert saga_method_2.name in meta_def.semantic_signature["aliases"]
