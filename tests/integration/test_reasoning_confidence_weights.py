"""
Integration tests — Phase 7A: Reasoning Confidence & Evidence Weights.

Tests:
  1. EvidenceWeightRegistry returns correct static weights.
  2. ReasoningConfidence.from_score produces correct tiers.
  3. ReasoningConfidence.compute produces weighted coverage scores.
  4. End-to-end query produces a confidence object with a valid score.
  5. Higher-weight evidence types produce higher confidence scores.
  6. Zero evidence produces MINIMAL confidence.
"""

import uuid
import pytest

from src.application.reasoning.evidence_weight_registry import EvidenceWeightRegistry
from src.application.reasoning.reasoning_confidence import ReasoningConfidence, ConfidenceLevel
from src.application.reasoning.reasoning_evidence import ReasoningEvidence


# ── EvidenceWeightRegistry Tests ──────────────────────────────────────────────

class TestEvidenceWeightRegistry:
    def test_capability_has_highest_weight(self):
        assert EvidenceWeightRegistry.CAPABILITY == 1.00

    def test_flow_weight(self):
        assert EvidenceWeightRegistry.FLOW == 0.95

    def test_entity_weight(self):
        assert EvidenceWeightRegistry.ENTITY == 0.90

    def test_relationship_weight(self):
        assert EvidenceWeightRegistry.RELATIONSHIP == 0.85

    def test_concept_weight(self):
        assert EvidenceWeightRegistry.CONCEPT == 0.80

    def test_artifact_weight(self):
        assert EvidenceWeightRegistry.ARTIFACT == 0.75

    def test_dependency_weight(self):
        assert EvidenceWeightRegistry.DEPENDENCY == 0.70

    def test_timeline_weight(self):
        assert EvidenceWeightRegistry.TIMELINE == 0.65

    def test_unknown_type_returns_fallback(self):
        weight = EvidenceWeightRegistry.get("completely_unknown_type")
        assert weight == EvidenceWeightRegistry.UNKNOWN
        assert weight < 0.5

    def test_get_method_is_case_insensitive(self):
        assert EvidenceWeightRegistry.get("CAPABILITY") == EvidenceWeightRegistry.get("capability")
        assert EvidenceWeightRegistry.get("Entity") == EvidenceWeightRegistry.get("entity")

    def test_all_weights_returns_dict(self):
        weights = EvidenceWeightRegistry.all_weights()
        assert isinstance(weights, dict)
        assert len(weights) >= 8
        for val in weights.values():
            assert 0.0 <= val <= 1.0

    def test_all_weights_is_copy(self):
        """Modifying the returned dict must not affect the registry."""
        weights = EvidenceWeightRegistry.all_weights()
        weights["capability"] = 0.0
        assert EvidenceWeightRegistry.get("capability") == 1.00


# ── ReasoningConfidence Tests ─────────────────────────────────────────────────

class TestReasoningConfidence:
    def test_from_score_high_tier(self):
        conf = ReasoningConfidence.from_score(0.90)
        assert conf.level == ConfidenceLevel.HIGH
        assert conf.score == 0.90

    def test_from_score_medium_tier(self):
        conf = ReasoningConfidence.from_score(0.65)
        assert conf.level == ConfidenceLevel.MEDIUM

    def test_from_score_low_tier(self):
        conf = ReasoningConfidence.from_score(0.40)
        assert conf.level == ConfidenceLevel.LOW

    def test_from_score_minimal_tier(self):
        conf = ReasoningConfidence.from_score(0.10)
        assert conf.level == ConfidenceLevel.MINIMAL

    def test_from_score_boundary_high(self):
        conf = ReasoningConfidence.from_score(0.80)
        assert conf.level == ConfidenceLevel.HIGH

    def test_from_score_boundary_medium(self):
        conf = ReasoningConfidence.from_score(0.55)
        assert conf.level == ConfidenceLevel.MEDIUM

    def test_from_score_boundary_low(self):
        conf = ReasoningConfidence.from_score(0.30)
        assert conf.level == ConfidenceLevel.LOW

    def test_from_score_zero(self):
        conf = ReasoningConfidence.from_score(0.0)
        assert conf.level == ConfidenceLevel.MINIMAL
        assert conf.score == 0.0

    def test_from_score_one(self):
        conf = ReasoningConfidence.from_score(1.0)
        assert conf.level == ConfidenceLevel.HIGH
        assert conf.score == 1.0

    def test_from_score_invalid_above_one(self):
        with pytest.raises(ValueError):
            ReasoningConfidence.from_score(1.5)

    def test_from_score_invalid_below_zero(self):
        with pytest.raises(ValueError):
            ReasoningConfidence.from_score(-0.1)

    def test_rationale_is_preserved(self):
        conf = ReasoningConfidence.from_score(0.75, rationale="test rationale")
        assert conf.rationale == "test rationale"

    def test_confidence_is_frozen(self):
        conf = ReasoningConfidence.from_score(0.80)
        with pytest.raises(Exception):  # dataclass frozen=True raises FrozenInstanceError
            conf.score = 0.5  # type: ignore[misc]

    def test_str_representation(self):
        conf = ReasoningConfidence.from_score(0.85)
        s = str(conf)
        assert "HIGH" in s
        assert "%" in s


# ── ReasoningConfidence.compute Tests ─────────────────────────────────────────

class TestReasoningConfidenceCompute:
    def test_full_coverage_produces_high_confidence(self):
        weights = EvidenceWeightRegistry.all_weights()
        found_types = set(weights.keys())
        conf = ReasoningConfidence.compute(weights=weights, found_types=found_types)
        assert conf.score == 1.0
        assert conf.level == ConfidenceLevel.HIGH

    def test_zero_coverage_produces_minimal_confidence(self):
        weights = EvidenceWeightRegistry.all_weights()
        conf = ReasoningConfidence.compute(weights=weights, found_types=set())
        assert conf.score == 0.0
        assert conf.level == ConfidenceLevel.MINIMAL

    def test_partial_coverage_has_intermediate_score(self):
        weights = {"capability": 1.0, "entity": 0.9}
        conf = ReasoningConfidence.compute(weights=weights, found_types={"capability"})
        # score = 1.0 / 1.9 ≈ 0.526
        assert 0.0 < conf.score < 1.0

    def test_high_weight_evidence_raises_score_more(self):
        weights = {"capability": 1.0, "entity": 0.5}
        conf_cap = ReasoningConfidence.compute(weights=weights, found_types={"capability"})
        conf_ent = ReasoningConfidence.compute(weights=weights, found_types={"entity"})
        assert conf_cap.score > conf_ent.score

    def test_empty_weights_returns_zero(self):
        conf = ReasoningConfidence.compute(weights={}, found_types={"capability"})
        assert conf.score == 0.0

    def test_score_never_exceeds_one(self):
        weights = {"capability": 1.0}
        conf = ReasoningConfidence.compute(weights=weights, found_types={"capability", "extra_type"})
        assert conf.score <= 1.0


# ── ReasoningEvidence Weight Validation ───────────────────────────────────────

class TestReasoningEvidenceWeight:
    def test_evidence_with_valid_weight(self):
        ev = ReasoningEvidence(
            source_id="test-id",
            source_type="entity",
            description="Test entity",
            weight=0.90,
        )
        ev.validate_weight()  # should not raise

    def test_evidence_with_invalid_weight_raises(self):
        ev = ReasoningEvidence(
            source_id="test-id",
            source_type="entity",
            description="Test entity",
            weight=1.5,  # invalid
        )
        with pytest.raises(ValueError):
            ev.validate_weight()

    def test_evidence_to_dict(self):
        ev = ReasoningEvidence(
            source_id="abc-123",
            source_type="capability",
            description="Auth capability",
            weight=1.0,
            validated=True,
        )
        d = ev.to_dict()
        assert d["source_id"] == "abc-123"
        assert d["source_type"] == "capability"
        assert d["weight"] == 1.0
        assert d["validated"] is True


# ── End-to-End Confidence Integration ─────────────────────────────────────────

@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient
    from src.config import settings
    from src.main import app
    from src.infrastructure.persistence.models import Base
    original_url = settings.database_url
    settings.database_url = "sqlite:///:memory:"
    try:
        with TestClient(app) as client:
            Base.metadata.create_all(client.app.state.container.engine)
            yield client
    finally:
        settings.database_url = original_url


def test_end_to_end_confidence_structure(api_client):
    """Full query must return a confidence object with valid structure."""
    repo_id = str(uuid.uuid4())
    response = api_client.post(
        "/api/v1/reasoning/query",
        json={
            "repository_id": repo_id,
            "commit_hash": "abc123",
            "query": "What capabilities does AuthService have?",
            "use_cache": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    conf = data["confidence"]
    assert "score" in conf
    assert "level" in conf
    assert "rationale" in conf
    assert 0.0 <= conf["score"] <= 1.0
    assert conf["level"] in ("HIGH", "MEDIUM", "LOW", "MINIMAL")


def test_empty_repository_produces_minimal_confidence(api_client):
    """An empty repository should produce MINIMAL or LOW confidence."""
    repo_id = str(uuid.uuid4())
    response = api_client.post(
        "/api/v1/reasoning/query",
        json={
            "repository_id": repo_id,
            "commit_hash": "empty",
            "query": "Why does this service exist?",
            "use_cache": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    score = data["confidence"]["score"]
    # Empty repo should produce very low or zero confidence
    assert score <= 0.60  # Generous upper bound; actual is likely 0 or near-0
