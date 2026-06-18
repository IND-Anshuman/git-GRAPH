"""
Integration tests — Phase 7A: Reasoning Query Planning & Strategy Resolution.

Tests:
  1. QueryPlanner classifies question types correctly.
  2. ReasoningStrategyRegistry resolves correct strategies.
  3. ReasoningCache stores and retrieves results correctly.
  4. ReasoningQueryEngine runs full pipeline on an empty repository (zero evidence path).
  5. /api/v1/reasoning/query endpoint responds with valid structure.
  6. /api/v1/reasoning/health endpoint is reachable.
"""

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app
from src.infrastructure.persistence.models import Base
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork

from src.application.reasoning.query_planner import QueryPlanner
from src.application.reasoning.reasoning_question_type import ReasoningQuestionType
from src.application.reasoning.reasoning_strategy_registry import ReasoningStrategyRegistry
from src.application.reasoning.reasoning_cache import ReasoningCache


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    """Return a FastAPI TestClient with an in-memory SQLite database."""
    original_url = settings.database_url
    settings.database_url = "sqlite:///:memory:"
    try:
        with TestClient(app) as client:
            Base.metadata.create_all(client.app.state.container.engine)
            yield client
    finally:
        settings.database_url = original_url


# ── QueryPlanner Tests ────────────────────────────────────────────────────────

class TestQueryPlanner:
    def setup_method(self):
        self.planner = QueryPlanner()

    def test_why_question_type(self):
        plan = self.planner.plan("Why does the AuthService exist?")
        assert plan.question_type == ReasoningQuestionType.WHY

    def test_blast_radius_question_type(self):
        plan = self.planner.plan("What is the blast radius of CheckoutService?")
        assert plan.question_type == ReasoningQuestionType.BLAST_RADIUS

    def test_root_cause_question_type(self):
        plan = self.planner.plan("What is the root cause of the payment failure?")
        assert plan.question_type == ReasoningQuestionType.ROOT_CAUSE

    def test_architecture_question_type(self):
        plan = self.planner.plan("What is the architecture of this system?")
        assert plan.question_type == ReasoningQuestionType.ARCHITECTURE

    def test_dependency_question_type(self):
        plan = self.planner.plan("What does OrderService depend on?")
        assert plan.question_type == ReasoningQuestionType.DEPENDENCY

    def test_ownership_question_type(self):
        plan = self.planner.plan("Who owns the authentication module?")
        assert plan.question_type == ReasoningQuestionType.OWNERSHIP

    def test_general_question_type_fallback(self):
        plan = self.planner.plan("Tell me about this codebase")
        assert plan.question_type == ReasoningQuestionType.GENERAL

    def test_plan_has_collect_scopes(self):
        plan = self.planner.plan("Why does this exist?")
        assert isinstance(plan.collect_scopes, list)
        assert len(plan.collect_scopes) > 0

    def test_plan_has_max_hops(self):
        plan = self.planner.plan("What is the blast radius of X?")
        assert plan.max_hops >= 2

    def test_blast_radius_has_higher_hops(self):
        blast_plan = self.planner.plan("What is the blast radius of UserService?")
        why_plan = self.planner.plan("Why does UserService exist?")
        assert blast_plan.max_hops >= why_plan.max_hops

    def test_empty_query_raises(self):
        with pytest.raises(ValueError):
            self.planner.plan("")

    def test_target_term_extracted(self):
        plan = self.planner.plan("Why does AuthService exist?")
        # Should extract 'AuthService' as the target term
        assert plan.target_term  # non-empty


# ── Strategy Registry Tests ───────────────────────────────────────────────────

class TestReasoningStrategyRegistry:
    def setup_method(self):
        self.registry = ReasoningStrategyRegistry.default()

    def test_registry_resolves_why(self):
        strategy = self.registry.resolve(ReasoningQuestionType.WHY)
        assert strategy.supports(ReasoningQuestionType.WHY)

    def test_registry_resolves_blast_radius(self):
        strategy = self.registry.resolve(ReasoningQuestionType.BLAST_RADIUS)
        assert strategy.supports(ReasoningQuestionType.BLAST_RADIUS)

    def test_registry_resolves_root_cause(self):
        strategy = self.registry.resolve(ReasoningQuestionType.ROOT_CAUSE)
        assert strategy.supports(ReasoningQuestionType.ROOT_CAUSE)

    def test_registry_resolves_counterfactual(self):
        strategy = self.registry.resolve(ReasoningQuestionType.COUNTERFACTUAL)
        assert strategy.supports(ReasoningQuestionType.COUNTERFACTUAL)

    def test_registry_resolves_architecture(self):
        strategy = self.registry.resolve(ReasoningQuestionType.ARCHITECTURE)
        assert strategy.supports(ReasoningQuestionType.ARCHITECTURE)

    def test_registry_has_registered_types(self):
        types = self.registry.registered_types()
        assert len(types) > 0
        assert ReasoningQuestionType.WHY in types

    def test_general_strategy_is_fallback(self):
        # GENERAL should always resolve
        strategy = self.registry.resolve(ReasoningQuestionType.GENERAL)
        assert strategy.supports(ReasoningQuestionType.GENERAL)

    def test_can_extend_with_new_strategy(self):
        """Verify that registering a new strategy works without modifying the registry."""
        class DriftStrategy:
            def supports(self, qt):
                return qt == ReasoningQuestionType.DRIFT

            def execute(self, context):
                raise NotImplementedError

        self.registry.register(DriftStrategy())
        strategy = self.registry.resolve(ReasoningQuestionType.DRIFT)
        assert strategy.supports(ReasoningQuestionType.DRIFT)


# ── Cache Tests ───────────────────────────────────────────────────────────────

class TestReasoningCache:
    def setup_method(self):
        self.cache = ReasoningCache(max_size=10)

    def test_cache_miss_returns_none(self):
        key = ReasoningCache.make_key("repo-1", "abc", ReasoningQuestionType.WHY, "why?")
        assert self.cache.get(key) is None

    def test_cache_put_and_get(self, api_client):
        """Store a real result in cache and retrieve it."""
        container = api_client.app.state.container
        engine = container.get_reasoning_query_engine()

        repo_id = str(uuid.uuid4())
        result = engine.query(
            repository_id=repo_id,
            commit_hash="test_commit_abc",
            query="Why does AuthService exist?",
            use_cache=False,
        )
        key = ReasoningCache.make_key(repo_id, "test_commit_abc", ReasoningQuestionType.WHY, "Why does AuthService exist?")
        self.cache.put(key, result)
        retrieved = self.cache.get(key)
        assert retrieved is not None
        assert retrieved.execution_id == result.execution_id

    def test_cache_invalidation(self, api_client):
        container = api_client.app.state.container
        engine = container.get_reasoning_query_engine()

        repo_id = str(uuid.uuid4())
        result = engine.query(
            repository_id=repo_id,
            commit_hash="abc",
            query="Why does X exist?",
            use_cache=False,
        )
        key = ReasoningCache.make_key(repo_id, "abc", ReasoningQuestionType.WHY, "Why does X exist?")
        self.cache.put(key, result)

        removed = self.cache.invalidate(repo_id)
        assert removed == 1
        assert self.cache.get(key) is None

    def test_cache_size_tracking(self, api_client):
        container = api_client.app.state.container
        engine = container.get_reasoning_query_engine()

        initial_size = self.cache.size()
        repo_id = str(uuid.uuid4())
        result = engine.query(
            repository_id=repo_id,
            commit_hash="xyz",
            query="Architecture overview?",
            use_cache=False,
        )
        key = ReasoningCache.make_key(repo_id, "xyz", ReasoningQuestionType.ARCHITECTURE, "Architecture overview?")
        self.cache.put(key, result)
        assert self.cache.size() == initial_size + 1

    def test_query_normalisation(self):
        """Cache keys should match despite whitespace variations."""
        key1 = ReasoningCache.make_key("r", "c", ReasoningQuestionType.WHY, "  Why does X exist?  ")
        key2 = ReasoningCache.make_key("r", "c", ReasoningQuestionType.WHY, "why does x exist?")
        assert key1 == key2


# ── API Endpoint Tests ────────────────────────────────────────────────────────

def test_reasoning_query_endpoint_returns_result(api_client):
    """The query endpoint must return a structured result even for an empty repo."""
    repo_id = str(uuid.uuid4())
    response = api_client.post(
        "/api/v1/reasoning/query",
        json={
            "repository_id": repo_id,
            "commit_hash": "abc1234",
            "query": "Why does AuthService exist?",
            "use_cache": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "execution_id" in data
    assert "answer" in data
    assert "confidence" in data
    assert "reasoning_chain" in data
    assert "provenance_graph" in data
    assert "limitations" in data
    assert "source_ids" in data


def test_reasoning_health_endpoint(api_client):
    """Health endpoint must return ok status and a list of registered strategies."""
    response = api_client.get("/api/v1/reasoning/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "reasoning_version" in data
    assert isinstance(data["registered_strategies"], list)
    assert len(data["registered_strategies"]) > 0


def test_reasoning_cache_status_endpoint(api_client):
    """Cache status endpoint must return cache_size field."""
    response = api_client.get("/api/v1/reasoning/cache/status")
    assert response.status_code == 200
    data = response.json()
    assert "cache_size" in data


def test_reasoning_cache_invalidation_endpoint(api_client):
    """Cache invalidation endpoint must return entries_removed."""
    repo_id = str(uuid.uuid4())
    response = api_client.delete(f"/api/v1/reasoning/cache/{repo_id}")
    assert response.status_code == 200
    data = response.json()
    assert "entries_removed" in data
    assert data["repository_id"] == repo_id
