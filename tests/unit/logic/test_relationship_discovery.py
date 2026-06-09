"""Unit tests for RelationshipDiscoveryEngine dynamic semantic relationship edge discovery."""

import pytest
import uuid
from sqlalchemy.orm import sessionmaker

from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.enums.relationship_type import RelationshipType
from src.application.semantic.calibration.calibration_engine import ConfidenceCalibrationEngine
from src.application.semantic.discovery.relationship_discovery_engine import RelationshipDiscoveryEngine
from src.application.semantic.isr.canonical_entity import CanonicalEntity
from src.application.semantic.isr.canonical_flow import CanonicalFlow


class DummyDatabaseEngine:
    def __init__(self, session_factory):
        self.session_factory = session_factory


@pytest.fixture
def uow(db_engine):
    session_factory = sessionmaker(bind=db_engine)
    db_mock = DummyDatabaseEngine(session_factory)
    return SQLAlchemyUnitOfWork(db_mock)


def test_relationship_discovery_rpc_route_matching(uow):
    """Test backend RPC endpoint matching using RouteNormalizer."""
    calibration = ConfidenceCalibrationEngine()
    engine = RelationshipDiscoveryEngine(uow, calibration)
    repo_id = RepositoryId.generate()

    # Create dummy entities representing dynamic API calls
    # 1. API Client entity calling a parameterized URL
    client_entity = CanonicalEntity(
        id=str(uuid.uuid4()),
        name="UserHttpClient",
        qualified_name="UserHttpClient",
        entity_type="APIClient",
        metadata={
            "routes": ["http://internal-service/users/{user_id}/profile"],
            "calls": ["requests.get"],
        },
    )

    # 2. Server-side API endpoint controller with a slightly different route parameter layout
    endpoint_entity = CanonicalEntity(
        id=str(uuid.uuid4()),
        name="GetUserProfileController",
        qualified_name="GetUserProfileController",
        entity_type="Controller",
        metadata={
            "http_route": "/api/v1/users/:id/profile",
            "route": "/api/v1/users/:id/profile",
        },
    )

    relationships = engine.discover_relationships(
        repository_id=repo_id,
        entities=[client_entity, endpoint_entity],
        behaviors=[],
        flows=[],
    )

    # Validate that they matched and created a CALLS_ENDPOINT relationship
    assert len(relationships) == 1
    rel = relationships[0]
    assert rel.relationship_type == RelationshipType.CALLS_ENDPOINT
    assert str(rel.source_seid.value) == client_entity.id
    assert str(rel.target_seid.value) == endpoint_entity.id
    assert rel.metadata["client_route"] == "http://internal-service/users/{user_id}/profile"
    assert rel.metadata["server_route"] == "/api/v1/users/:id/profile"
    assert "evidence" in rel.metadata


def test_relationship_discovery_ai_native_flows(uow):
    """Test AI-native relationships extracted from canonical execution flows."""
    calibration = ConfidenceCalibrationEngine()
    engine = RelationshipDiscoveryEngine(uow, calibration)
    repo_id = RepositoryId.generate()

    # Seed AI-Native entity mapping
    agent = CanonicalEntity(
        id=str(uuid.uuid4()),
        name="SupportAgent",
        qualified_name="SupportAgent",
        entity_type="Agent",
    )
    model = CanonicalEntity(
        id=str(uuid.uuid4()),
        name="GPT4oModel",
        qualified_name="GPT4oModel",
        entity_type="Model",
    )
    tool = CanonicalEntity(
        id=str(uuid.uuid4()),
        name="WebSearchTool",
        qualified_name="WebSearchTool",
        entity_type="Tool",
    )
    vector_db = CanonicalEntity(
        id=str(uuid.uuid4()),
        name="PineconeRetriever",
        qualified_name="PineconeRetriever",
        entity_type="VectorDB",
    )
    memory_store = CanonicalEntity(
        id=str(uuid.uuid4()),
        name="RedisMemory",
        qualified_name="RedisMemory",
        entity_type="Memory",
    )

    # Construct execution flows linking Agent -> Model, Agent -> Tool, etc.
    flow1 = CanonicalFlow(
        id="flow-1",
        flow_type="LLM_CALL",
        source_entity_id=agent.id,
        target_entity_id=model.id,
        intermediate_entities=[],
        confidence=0.95,
    )
    flow2 = CanonicalFlow(
        id="flow-2",
        flow_type="TOOL_EXECUTION",
        source_entity_id=agent.id,
        target_entity_id=tool.id,
        intermediate_entities=[],
        confidence=0.90,
    )
    flow3 = CanonicalFlow(
        id="flow-3",
        flow_type="RETRIEVAL",
        source_entity_id=agent.id,
        target_entity_id=vector_db.id,
        intermediate_entities=[],
        confidence=0.88,
    )
    flow4 = CanonicalFlow(
        id="flow-4",
        flow_type="STATE_WRITE",
        source_entity_id=agent.id,
        target_entity_id=memory_store.id,
        intermediate_entities=[],
        confidence=0.92,
    )

    entities = [agent, model, tool, vector_db, memory_store]
    flows = [flow1, flow2, flow3, flow4]

    relationships = engine.discover_relationships(
        repository_id=repo_id,
        entities=entities,
        behaviors=[],
        flows=flows,
    )

    assert len(relationships) == 4
    rel_types = [r.relationship_type for r in relationships]
    assert RelationshipType.CALLS_MODEL in rel_types
    assert RelationshipType.USES_TOOL in rel_types
    assert RelationshipType.RETRIEVES_CONTEXT in rel_types
    assert RelationshipType.WRITES_MEMORY in rel_types


def test_relationship_discovery_messaging_and_frontend(uow):
    """Test distributed messaging and frontend UI relationship mappings."""
    calibration = ConfidenceCalibrationEngine()
    engine = RelationshipDiscoveryEngine(uow, calibration)
    repo_id = RepositoryId.generate()

    # Messaging
    producer = CanonicalEntity(
        id=str(uuid.uuid4()), name="OrderService", qualified_name="OrderService", entity_type="Producer"
    )
    topic = CanonicalEntity(
        id=str(uuid.uuid4()), name="order-events", qualified_name="order-events", entity_type="Topic"
    )
    consumer = CanonicalEntity(
        id=str(uuid.uuid4()), name="BillingService", qualified_name="BillingService", entity_type="Consumer"
    )

    flow_pub = CanonicalFlow(
        id="flow-pub",
        flow_type="KAFKA_PUBLISH",
        source_entity_id=producer.id,
        target_entity_id=topic.id,
        intermediate_entities=[],
        confidence=0.95,
    )
    flow_sub = CanonicalFlow(
        id="flow-sub",
        flow_type="KAFKA_CONSUME",
        source_entity_id=consumer.id,
        target_entity_id=topic.id,
        intermediate_entities=[],
        confidence=0.95,
    )

    # Frontend Component -> Hook
    component = CanonicalEntity(
        id=str(uuid.uuid4()), name="UserDashboard", qualified_name="UserDashboard", entity_type="Component"
    )
    hook = CanonicalEntity(
        id=str(uuid.uuid4()), name="useAuth", qualified_name="useAuth", entity_type="Hook"
    )

    flow_hook = CanonicalFlow(
        id="flow-hook",
        flow_type="REACT_HOOK",
        source_entity_id=component.id,
        target_entity_id=hook.id,
        intermediate_entities=[],
        confidence=0.90,
    )

    entities = [producer, topic, consumer, component, hook]
    flows = [flow_pub, flow_sub, flow_hook]

    relationships = engine.discover_relationships(
        repository_id=repo_id,
        entities=entities,
        behaviors=[],
        flows=flows,
    )

    assert len(relationships) == 3
    rel_types = [r.relationship_type for r in relationships]
    assert RelationshipType.PUBLISHES_TO_TOPIC in rel_types
    assert RelationshipType.CONSUMES_FROM_TOPIC in rel_types
    assert RelationshipType.USES_HOOK in rel_types
