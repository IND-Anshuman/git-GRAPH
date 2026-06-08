"""Unit tests for Phase 4 concept graph metrics engine."""

import uuid
from datetime import datetime, timezone
import pytest

from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.entities.concept_relationship import ConceptRelationship
from src.domain.enums.concept_relationship_type import ConceptRelationshipType
from src.domain.value_objects.repository_id import RepositoryId
from src.application.services.concept_metrics_engine import ConceptMetricsEngine


class MockLogicVersion:
    def __init__(self, id, code_entity_seid, logic_signature_id, commit_hash):
        self.id = id
        self.code_entity_seid = code_entity_seid
        self.logic_signature_id = logic_signature_id
        self.commit_hash = commit_hash
        self.overall_confidence = 0.80


class MockLogicSignature:
    def __init__(self, file_path):
        self.canonical_name = "test_pattern"
        self.file_path = file_path


class MockUow:
    def __init__(self, lvs, sigs):
        self.lvs = lvs
        self.sigs = sigs

    @property
    def logic_versions(self):
        class MockLVRepo:
            def get_by_id(sub_self, lid):
                return self.lvs.get(lid)
        return MockLVRepo()

    @property
    def logic_signatures(self):
        class MockSigRepo:
            def get_by_id(sub_self, sid):
                return self.sigs.get(sid)
        return MockSigRepo()


def test_concept_metrics_centrality_and_pagerank():
    # Setup mock data for 3 concepts with relationships: C1 -> C2 -> C3
    repo_id = RepositoryId.generate()
    commit_hash = "hash1"
    now = datetime.now(timezone.utc)

    # 1. Create Nodes and Versions
    c1_id = uuid.uuid4()
    c1_node = ConceptNode(c1_id, repo_id, "security.auth", "Auth", "Auth", True, now, now)
    c1_ver = ConceptVersion(uuid.uuid4(), c1_id, commit_hash, 1, 0.90, True, {}, now)

    c2_id = uuid.uuid4()
    c2_node = ConceptNode(c2_id, repo_id, "data.persist", "Persist", "Persist", True, now, now)
    c2_ver = ConceptVersion(uuid.uuid4(), c2_id, commit_hash, 1, 0.85, True, {}, now)

    c3_id = uuid.uuid4()
    c3_node = ConceptNode(c3_id, repo_id, "reliability.retry", "Retry", "Retry", True, now, now)
    c3_ver = ConceptVersion(uuid.uuid4(), c3_id, commit_hash, 1, 0.80, True, {}, now)

    # 2. Setup evidences (LogicVersions)
    lv1_id = uuid.uuid4()
    lv2_id = uuid.uuid4()
    lv3_id = uuid.uuid4()

    ev1 = ConceptEvidence(uuid.uuid4(), c1_ver.id, "LOGIC_VERSION", lv1_id, 0.90, {}, now)
    ev2 = ConceptEvidence(uuid.uuid4(), c2_ver.id, "LOGIC_VERSION", lv2_id, 0.85, {}, now)
    ev3 = ConceptEvidence(uuid.uuid4(), c3_ver.id, "LOGIC_VERSION", lv3_id, 0.80, {}, now)

    detected_concepts = [
        (c1_node, c1_ver, [ev1]),
        (c2_node, c2_ver, [ev2]),
        (c3_node, c3_ver, [ev3]),
    ]

    # 3. Setup UoW mocks for resolving entities/files
    class SEIDMock:
        def __init__(self, val):
            self.value = val

    lvs = {
        lv1_id: MockLogicVersion(lv1_id, SEIDMock("func:verify"), uuid.uuid4(), commit_hash),
        lv2_id: MockLogicVersion(lv2_id, SEIDMock("func:save"), uuid.uuid4(), commit_hash),
        lv3_id: MockLogicVersion(lv3_id, SEIDMock("func:retry"), uuid.uuid4(), commit_hash),
    }

    sigs = {
        lvs[lv1_id].logic_signature_id: MockLogicSignature("src/auth.py"),
        lvs[lv2_id].logic_signature_id: MockLogicSignature("src/db.py"),
        lvs[lv3_id].logic_signature_id: MockLogicSignature("src/utils.py"),
    }

    uow = MockUow(lvs, sigs)

    # 4. Setup relationships: C1 depends_on C2, C2 depends_on C3
    rel1 = ConceptRelationship(
        id=uuid.uuid4(),
        repository_id=repo_id,
        commit_hash=commit_hash,
        from_concept_id=c1_id,
        to_concept_id=c2_id,
        relationship_type=ConceptRelationshipType.DEPENDS_ON,
        confidence=0.85,
        metadata={}
    )
    rel2 = ConceptRelationship(
        id=uuid.uuid4(),
        repository_id=repo_id,
        commit_hash=commit_hash,
        from_concept_id=c2_id,
        to_concept_id=c3_id,
        relationship_type=ConceptRelationshipType.DEPENDS_ON,
        confidence=0.80,
        metadata={}
    )

    engine = ConceptMetricsEngine()
    metrics = engine.compute_metrics(uow, detected_concepts, [rel1, rel2])

    assert len(metrics) == 3

    # Map results by concept_version_id
    metrics_map = {m.concept_version_id: m for m in metrics}

    # Verify size metrics
    c1_metrics = metrics_map[c1_ver.id]
    assert c1_metrics.entity_count == 1
    assert c1_metrics.file_count == 1

    # Verify Degree Centrality
    # C2 has 1 incoming link (from C1) and 1 outgoing link (to C3). Sum degree = 2. N = 3. Centrality = 2 / 2 = 1.0.
    c2_metrics = metrics_map[c2_ver.id]
    assert c2_metrics.degree_centrality == 1.0
    assert c2_metrics.in_degree == 1
    assert c2_metrics.out_degree == 1

    # Verify PageRank Centrality
    # PageRank scores must sum to approximately 1.0
    pr_sum = sum(m.pagerank_score for m in metrics)
    assert pytest.approx(pr_sum, 0.01) == 1.0

    # Verify Betweenness Centrality
    # C2 lies on the shortest path between C1 and C3, so it should have higher betweenness centrality.
    assert c2_metrics.betweenness_centrality > 0.0

    # Verify Systemic Impact Score
    # C3 is at the bottom, so C1 and C2 depend on it transitively. Impact of C3 should be highest.
    c3_metrics = metrics_map[c3_ver.id]
    assert c3_metrics.impact_score > c1_metrics.impact_score
