import uuid
from datetime import datetime, timezone
from src.application.decision_intelligence.decision_discovery_engine import DecisionDiscoveryEngine
from src.application.decision_intelligence.repository_memory import RepositoryMemory
from src.application.decision_intelligence.repository_event import RepositoryEvent, RepositoryEventType, RepositoryEventSource
from src.application.decision_intelligence.decision_type import DecisionType
from src.application.decision_intelligence.decision_status import DecisionStatus

class DummyRegistry:
    def __init__(self, matches=None):
        self.matches = matches or []

    def match_patterns(self, text):
        return self.matches

class DummyNode:
    def __init__(self, node_id, title):
        self.id = node_id
        self.title = title

class DummyGraph:
    def __init__(self, nodes):
        self.nodes = nodes

def test_discover_from_memory_builtin_kafka():
    dec_reg = DummyRegistry()
    int_reg = DummyRegistry()
    engine = DecisionDiscoveryEngine(dec_reg, int_reg)
    
    event_id = uuid.uuid4()
    event = RepositoryEvent(
        event_id=event_id,
        event_type=RepositoryEventType.DEPENDENCY_INTRODUCED,
        source=RepositoryEventSource.COMMIT,
        repository_id="test-repo",
        commit_hash="abc1234",
        description="Introduced dependency: kafka-python==2.0.2",
        occurred_at=datetime.now(timezone.utc),
        metadata={"dependency_name": "kafka-python"}
    )
    
    memory = RepositoryMemory(
        repository_id="test-repo",
        events=[event],
        technology_introductions=["abc1234"]
    )
    
    decisions = engine.discover_from_memory(memory, [])
    
    assert len(decisions) == 1
    decision = decisions[0]
    assert decision.repository_id == "test-repo"
    assert decision.decision_type == DecisionType.TECHNOLOGY_ADOPTION
    assert decision.status == DecisionStatus.ACTIVE
    assert "Apache Kafka" in decision.name
    assert decision.confidence is not None
    assert decision.confidence.score > 0.0

def test_discover_from_memory_with_adr():
    dec_reg = DummyRegistry()
    int_reg = DummyRegistry()
    engine = DecisionDiscoveryEngine(dec_reg, int_reg)
    
    event_id = uuid.uuid4()
    event = RepositoryEvent(
        event_id=event_id,
        event_type=RepositoryEventType.DEPENDENCY_INTRODUCED,
        source=RepositoryEventSource.COMMIT,
        repository_id="test-repo",
        commit_hash="abc1234",
        description="Introduced dependency: kafka-python==2.0.2",
        occurred_at=datetime.now(timezone.utc),
        metadata={"dependency_name": "kafka-python"}
    )
    
    memory = RepositoryMemory(
        repository_id="test-repo",
        events=[event]
    )
    
    adr_node = DummyNode(uuid.uuid4(), "ADR-001: Adopt Apache Kafka for streaming")
    adr_graph = DummyGraph([adr_node])
    
    decisions = engine.discover_from_memory(memory, [adr_graph])
    
    assert len(decisions) == 1
    decision = decisions[0]
    assert len(decision.supporting_evidence.supporting_documents) == 1
    assert decision.supporting_evidence.supporting_documents[0] == str(adr_node.id)

def test_discover_from_memory_registry_match():
    # Test fallback to decision registry patterns for unknown tech
    mock_pattern = {
        "id": "my-custom-framework",
        "display_name": "Custom Framework",
        "decision_type": "TECHNOLOGY_ADOPTION",
        "intent_hints": ["SCALABILITY"]
    }
    dec_reg = DummyRegistry(matches=[mock_pattern])
    int_reg = DummyRegistry()
    engine = DecisionDiscoveryEngine(dec_reg, int_reg)
    
    event_id = uuid.uuid4()
    event = RepositoryEvent(
        event_id=event_id,
        event_type=RepositoryEventType.DEPENDENCY_INTRODUCED,
        source=RepositoryEventSource.COMMIT,
        repository_id="test-repo",
        commit_hash="abc1234",
        description="Introduced dependency: my-custom-framework",
        occurred_at=datetime.now(timezone.utc),
        metadata={"dependency_name": "my-custom-framework"}
    )
    
    memory = RepositoryMemory(
        repository_id="test-repo",
        events=[event]
    )
    
    decisions = engine.discover_from_memory(memory, [])
    assert len(decisions) == 1
    assert decisions[0].name == "Adopt Custom Framework"
