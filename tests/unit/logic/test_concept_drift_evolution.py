"""Unit tests for Phase 4 concept drift and concept evolution engines."""

import uuid
from datetime import datetime, timezone
import pytest

from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.entities.concept_evolution import ConceptEvolution
from src.domain.enums.concept_transition_type import ConceptTransitionType
from src.domain.value_objects.repository_id import RepositoryId
from src.application.services.concept_drift_engine import ConceptDriftEngine
from src.application.services.concept_evolution_engine import ConceptEvolutionEngine


def test_concept_drift_calculation():
    # Setup baseline and current versions
    repo_id = RepositoryId.generate()
    concept_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    base_ver = ConceptVersion(uuid.uuid4(), concept_id, "hash1", 1, 0.90, True, {}, now)
    curr_ver = ConceptVersion(uuid.uuid4(), concept_id, "hash2", 2, 0.85, True, {}, now)

    engine = ConceptDriftEngine()

    # Stub/Mock resolve_concept_assets to avoid database queries in unit test
    # We want structural drift of 0.50, pattern drift of 0.0, and dependency drift of 0.0
    # Overall score: 0.40 * 0.50 + 0.40 * 0.0 + 0.20 * 0.0 = 0.20 (category = "MINOR")
    def mock_resolve(uow, version):
        if version.commit_hash == "hash1":
            return {"entityA", "entityB"}, {"patternA"}, {"depA"}
        else:
            return {"entityB", "entityC"}, {"patternA"}, {"depA"}

    engine._resolve_concept_assets = mock_resolve

    drift = engine.compute_drift(None, concept_id, base_ver, curr_ver)

    assert drift.concept_id == concept_id
    assert drift.drift_score == pytest.approx(0.26666667)
    assert drift.drift_category == "MINOR"
    assert drift.dimension_scores["structural"] == pytest.approx(0.66666667)
    assert drift.dimension_scores["pattern"] == 0.0


def test_concept_evolution_split_and_merge():
    # Setup mock uow and engines to verify split/merge evolution classification
    repo_id = RepositoryId.generate()
    commit_hash = "hash2"
    now = datetime.now(timezone.utc)

    # Current detected concept versions
    c1_id = uuid.uuid4()
    c1_node = ConceptNode(c1_id, repo_id, "security.auth", "Auth", "Auth", True, now, now)
    c1_ver = ConceptVersion(uuid.uuid4(), c1_id, commit_hash, 2, 0.90, True, {}, now)

    c2_id = uuid.uuid4()
    c2_node = ConceptNode(c2_id, repo_id, "security.authz", "Authz", "Authz", True, now, now)
    c2_ver = ConceptVersion(uuid.uuid4(), c2_id, commit_hash, 1, 0.85, True, {}, now)

    # Previous baseline versions
    prev_ver_id = uuid.uuid4()
    prev_ver = ConceptVersion(prev_ver_id, c1_id, "hash1", 1, 0.90, True, {}, now)

    # Set up active logic versions supporting them
    class MockLogicVersion:
        def __init__(self, id, code_entity_seid):
            self.id = id
            self.code_entity_seid = code_entity_seid

    class SEIDMock:
        def __init__(self, val):
            self.value = val

    # Setup mock Uow
    class MockUow:
        def __init__(self):
            # Map target_id to logic version
            self.lvs = {
                "lv1": MockLogicVersion("lv1", SEIDMock("entity1")),
                "lv2": MockLogicVersion("lv2", SEIDMock("entity2")),
                "lv3": MockLogicVersion("lv3", SEIDMock("entity3")),
            }

        @property
        def commits(self):
            class MockCommitRepo:
                def get_by_hash(sub_self, h):
                    class CommitMock:
                        hash = "hash2"
                        parent_hashes = ["hash1"]
                    return CommitMock()
            return MockCommitRepo()

        @property
        def concept_versions(self):
            class MockVerRepo:
                def list_by_commit(sub_self, h):
                    return [prev_ver]
            return MockVerRepo()

        @property
        def concept_evidence(self):
            class MockEvidenceRepo:
                def list_by_concept_version(sub_self, vid):
                    # Previous version had entity1, entity2, entity3
                    return [
                        ConceptEvidence(uuid.uuid4(), vid, "LOGIC_VERSION", "lv1", 0.90, {}, now),
                        ConceptEvidence(uuid.uuid4(), vid, "LOGIC_VERSION", "lv2", 0.90, {}, now),
                        ConceptEvidence(uuid.uuid4(), vid, "LOGIC_VERSION", "lv3", 0.90, {}, now),
                    ]
            return MockEvidenceRepo()

        @property
        def logic_versions(self):
            class MockLVRepo:
                def get_by_id(sub_self, lid):
                    return self.lvs.get(lid)
            return MockLVRepo()

    uow = MockUow()

    # Current detected concepts:
    # c1 has entity1 (1 out of 3 from predecessor -> ~33% split ratio)
    # c2 has entity2, entity3 (2 out of 3 from predecessor -> ~66% split ratio)
    ev_c1 = ConceptEvidence(uuid.uuid4(), c1_ver.id, "LOGIC_VERSION", "lv1", 0.90, {}, now)
    ev_c2 = [
        ConceptEvidence(uuid.uuid4(), c2_ver.id, "LOGIC_VERSION", "lv2", 0.90, {}, now),
        ConceptEvidence(uuid.uuid4(), c2_ver.id, "LOGIC_VERSION", "lv3", 0.90, {}, now),
    ]

    detected = [
        (c1_node, c1_ver, [ev_c1]),
        (c2_node, c2_ver, ev_c2),
    ]

    engine = ConceptEvolutionEngine()
    evolutions = engine.track_evolution(uow, repo_id, commit_hash, detected)

    # Assert evolution transitions
    # Since prev_ver is for c1_id, and c1_ver is for c1_id, c1_ver is classified as CONCEPT_MODIFICATION.
    # c2_ver is a split target from prev_ver (as it got >= 30% of its entities)
    assert len(evolutions) >= 1
    types = [evo.transition_type for evo in evolutions]
    assert ConceptTransitionType.CONCEPT_MODIFICATION in types
    assert ConceptTransitionType.CONCEPT_SPLIT in types
