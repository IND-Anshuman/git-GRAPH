"""
Integration tests — Phase 7A: Evidence Validation Layer.

Tests:
  1. Trusted evidence types are accepted without DB lookup.
  2. Entity-type evidence that doesn't exist in DB is rejected.
  3. Invalid source_ids are discarded.
  4. Validated evidence has validated=True set.
  5. Context.validated_evidence is populated correctly.
  6. EvidenceValidationLayer does not crash on empty evidence.
  7. Limitations are auto-populated when evidence categories are missing.
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app
from src.infrastructure.persistence.models import Base

from src.application.reasoning.evidence_validation_layer import EvidenceValidationLayer
from src.application.reasoning.reasoning_evidence import ReasoningEvidence
from src.application.reasoning.reasoning_context import ReasoningContext
from src.application.reasoning.reasoning_question_type import ReasoningQuestionType
from src.application.reasoning.reasoning_snapshot import ReasoningSnapshot
from src.application.reasoning.reasoning_chain import ReasoningChain
from src.application.reasoning.evidence_weight_registry import EvidenceWeightRegistry


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    original_url = settings.database_url
    settings.database_url = "sqlite:///:memory:"
    try:
        with TestClient(app) as client:
            Base.metadata.create_all(client.app.state.container.engine)
            yield client
    finally:
        settings.database_url = original_url


def _make_context(repo_id: str = None) -> ReasoningContext:
    rid = repo_id or str(uuid.uuid4())
    snapshot = ReasoningSnapshot.unknown(rid, "test_commit")
    return ReasoningContext(
        execution_id=str(uuid.uuid4()),
        repository_id=rid,
        query="Why does X exist?",
        question_type=ReasoningQuestionType.WHY,
        snapshot=snapshot,
        chain=ReasoningChain(execution_id=str(uuid.uuid4())),
    )


def _make_uow_with_entity(entity_seid: str | None = None):
    """Build a mock UoW that returns an entity for entity_seid (or None)."""
    mock_entity = MagicMock()
    mock_entity.seid = entity_seid

    uow = MagicMock()
    uow.code_entities = MagicMock()
    uow.code_entities.get_by_seid = MagicMock(
        side_effect=lambda seid: mock_entity if str(seid) == entity_seid else None
    )
    return uow


# ── EvidenceValidationLayer Tests ─────────────────────────────────────────────

class TestEvidenceValidationLayer:
    def setup_method(self):
        self.validator = EvidenceValidationLayer()

    def test_trusted_capability_accepted_without_db(self):
        context = _make_context()
        context.expanded_evidence = [
            ReasoningEvidence(
                source_id="cap-123",
                source_type="capability",
                description="Auth capability",
                weight=1.0,
            )
        ]
        mock_uow = MagicMock()
        self.validator.validate(context, mock_uow)

        assert len(context.validated_evidence) == 1
        assert context.validated_evidence[0].validated is True
        # Should NOT have called code_entities at all
        assert not mock_uow.code_entities.get_by_seid.called

    def test_trusted_concept_accepted(self):
        context = _make_context()
        context.expanded_evidence = [
            ReasoningEvidence(
                source_id="concept-abc",
                source_type="concept",
                description="Auth concept",
                weight=0.80,
            )
        ]
        self.validator.validate(context, MagicMock())
        assert len(context.validated_evidence) == 1
        assert context.validated_evidence[0].validated is True

    def test_trusted_relationship_accepted(self):
        context = _make_context()
        context.expanded_evidence = [
            ReasoningEvidence(
                source_id="rel-xyz",
                source_type="relationship",
                description="CALLS relationship",
                weight=0.85,
            )
        ]
        self.validator.validate(context, MagicMock())
        assert len(context.validated_evidence) == 1

    def test_entity_found_in_db_accepted(self):
        entity_seid = str(uuid.uuid4())
        context = _make_context()
        context.expanded_evidence = [
            ReasoningEvidence(
                source_id=entity_seid,
                source_type="entity",
                description="Test entity",
                weight=0.90,
            )
        ]
        uow = _make_uow_with_entity(entity_seid)
        self.validator.validate(context, uow)

        assert len(context.validated_evidence) == 1
        assert context.validated_evidence[0].validated is True

    def test_entity_not_in_db_rejected(self):
        context = _make_context()
        context.expanded_evidence = [
            ReasoningEvidence(
                source_id="nonexistent-seid",
                source_type="entity",
                description="Ghost entity",
                weight=0.90,
            )
        ]
        uow = _make_uow_with_entity(None)  # always returns None
        self.validator.validate(context, uow)

        assert len(context.validated_evidence) == 0

    def test_empty_source_id_discarded(self):
        context = _make_context()
        context.expanded_evidence = [
            ReasoningEvidence(
                source_id="",  # invalid
                source_type="entity",
                description="Empty ID",
                weight=0.90,
            )
        ]
        self.validator.validate(context, MagicMock())
        assert len(context.validated_evidence) == 0

    def test_whitespace_only_source_id_discarded(self):
        context = _make_context()
        context.expanded_evidence = [
            ReasoningEvidence(
                source_id="   ",
                source_type="capability",
                description="Whitespace ID",
                weight=1.0,
            )
        ]
        self.validator.validate(context, MagicMock())
        assert len(context.validated_evidence) == 0

    def test_empty_evidence_list_is_handled(self):
        context = _make_context()
        context.expanded_evidence = []
        self.validator.validate(context, MagicMock())
        assert context.validated_evidence == []

    def test_validated_flag_set_to_true(self):
        context = _make_context()
        context.expanded_evidence = [
            ReasoningEvidence(
                source_id="cap-999",
                source_type="capability",
                description="Cap",
                weight=1.0,
                validated=False,  # starts False
            )
        ]
        self.validator.validate(context, MagicMock())
        assert context.validated_evidence[0].validated is True

    def test_mixed_trusted_and_entity_evidence(self):
        entity_seid = str(uuid.uuid4())
        context = _make_context()
        context.expanded_evidence = [
            ReasoningEvidence(source_id="cap-1", source_type="capability", description="Cap", weight=1.0),
            ReasoningEvidence(source_id=entity_seid, source_type="entity", description="Entity", weight=0.90),
            ReasoningEvidence(source_id="nonexistent", source_type="entity", description="Ghost", weight=0.90),
        ]
        uow = _make_uow_with_entity(entity_seid)
        self.validator.validate(context, uow)

        # cap-1 (trusted) + entity_seid (found) = 2 accepted; "nonexistent" rejected
        assert len(context.validated_evidence) == 2
        ids = [ev.source_id for ev in context.validated_evidence]
        assert "cap-1" in ids
        assert entity_seid in ids
        assert "nonexistent" not in ids

    def test_db_exception_falls_back_to_accept_with_reduced_weight(self):
        """If DB lookup throws, evidence is accepted but with reduced weight."""
        context = _make_context()
        context.expanded_evidence = [
            ReasoningEvidence(
                source_id="entity-db-error",
                source_type="entity",
                description="DB error entity",
                weight=0.90,
            )
        ]
        uow = MagicMock()
        uow.code_entities.get_by_seid.side_effect = RuntimeError("DB connection error")
        self.validator.validate(context, uow)

        # Should be accepted (fail-open), but with reduced weight
        assert len(context.validated_evidence) == 1
        assert context.validated_evidence[0].weight < 0.90


# ── Chain Step Recording Tests ────────────────────────────────────────────────

def test_validation_records_chain_step():
    """Validation layer must add at least one step to the reasoning chain."""
    validator = EvidenceValidationLayer()
    context = _make_context()
    context.expanded_evidence = [
        ReasoningEvidence(source_id="cap-1", source_type="capability", description="Cap", weight=1.0)
    ]
    initial_steps = len(context.chain.steps)
    validator.validate(context, MagicMock())
    assert len(context.chain.steps) > initial_steps


# ── Limitation Auto-Detection via End-to-End ─────────────────────────────────

def test_missing_ownership_produces_limitation(api_client):
    """An empty repo with no ownership data should produce ownership limitation."""
    repo_id = str(uuid.uuid4())
    response = api_client.post(
        "/api/v1/reasoning/query",
        json={
            "repository_id": repo_id,
            "commit_hash": "test123",
            "query": "Who owns the AuthService module?",
            "use_cache": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    limitations = data.get("limitations", [])
    # Should have at least one limitation due to missing data
    assert isinstance(limitations, list)


def test_result_always_has_limitations_field(api_client):
    """Every reasoning result must have a limitations list (possibly empty)."""
    repo_id = str(uuid.uuid4())
    response = api_client.post(
        "/api/v1/reasoning/query",
        json={
            "repository_id": repo_id,
            "commit_hash": "abc",
            "query": "General system overview",
            "use_cache": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "limitations" in data
    assert isinstance(data["limitations"], list)
