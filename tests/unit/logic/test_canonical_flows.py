"""Unit tests for canonical flows tracing and sequence assembly."""

import pytest
from src.application.semantic.isr import CanonicalEntity
from src.application.semantic.behavior_registry.canonical_registry import CanonicalRegistry
from src.application.semantic.normalization.semantic_normalizer import SemanticNormalizer
from src.application.semantic.type_resolution.type_resolution_engine import TypeResolutionEngine


def test_trace_flow_web_request():
    """Verify that a sequence of entities is correctly assembled into a Web Request Flow."""
    registry = CanonicalRegistry()
    type_engine = TypeResolutionEngine()
    normalizer = SemanticNormalizer(registry, type_engine)

    # Define entities
    endpoint = CanonicalEntity(
        id="ent-endpoint-uuid",
        name="login",
        qualified_name="App.Controllers.AuthController.login",
        entity_type="APIEndpoint"
    )
    service = CanonicalEntity(
        id="ent-service-uuid",
        name="VerifyPassword",
        qualified_name="App.Services.AuthService.VerifyPassword",
        entity_type="Service"
    )
    repository = CanonicalEntity(
        id="ent-repo-uuid",
        name="GetUser",
        qualified_name="App.Repositories.UserRepository.GetUser",
        entity_type="Repository"
    )
    db_table = CanonicalEntity(
        id="ent-db-uuid",
        name="users",
        qualified_name="Database.Tables.users",
        entity_type="DatabaseTable"
    )

    flow = normalizer.trace_flow(
        flow_type="REQUEST_RESPONSE_FLOW",
        entities=[endpoint, service, repository, db_table],
        confidence=0.95,
        metadata={"http_route": "/api/auth/login", "db_sink_table": "users"}
    )

    assert flow is not None
    assert flow.flow_type == "REQUEST_RESPONSE_FLOW"
    assert flow.source_entity_id == endpoint.id
    assert flow.target_entity_id == db_table.id
    assert flow.intermediate_entities == [service.id, repository.id]
    assert flow.confidence == 0.95
    assert flow.metadata.get("http_route") == "/api/auth/login"
    assert flow.metadata.get("db_sink_table") == "users"


def test_trace_flow_ai_agent():
    """Verify that an AI Agent workflow flow sequence is correctly traced."""
    registry = CanonicalRegistry()
    type_engine = TypeResolutionEngine()
    normalizer = SemanticNormalizer(registry, type_engine)

    agent = CanonicalEntity(
        id="ent-agent-uuid",
        name="researcher",
        qualified_name="App.Agents.researcher",
        entity_type="Agent"
    )
    vector_db = CanonicalEntity(
        id="ent-vectordb-uuid",
        name="knowledge_store",
        qualified_name="App.Storage.knowledge_store",
        entity_type="VectorDB"
    )
    model = CanonicalEntity(
        id="ent-llm-uuid",
        name="gpt-4o",
        qualified_name="App.Models.gpt_4o",
        entity_type="Model"
    )

    flow = normalizer.trace_flow(
        flow_type="AI_AGENT_WORKFLOW",
        entities=[agent, vector_db, model],
        confidence=0.88,
        metadata={"temperature": 0.2}
    )

    assert flow is not None
    assert flow.flow_type == "AI_AGENT_WORKFLOW"
    assert flow.source_entity_id == agent.id
    assert flow.target_entity_id == model.id
    assert flow.intermediate_entities == [vector_db.id]
    assert flow.confidence == 0.88
    assert flow.metadata.get("temperature") == 0.2


def test_trace_flow_too_short():
    """Verify that tracing fails if less than two entities are provided."""
    registry = CanonicalRegistry()
    type_engine = TypeResolutionEngine()
    normalizer = SemanticNormalizer(registry, type_engine)

    entity = CanonicalEntity(
        id="ent-uuid",
        name="single",
        qualified_name="single",
        entity_type="Class"
    )
    flow = normalizer.trace_flow("FLOW", [entity])
    assert flow is None
