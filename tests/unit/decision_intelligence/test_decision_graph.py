import uuid
from datetime import datetime, timezone
from src.application.decision_intelligence.decision import Decision
from src.application.decision_intelligence.decision_type import DecisionType
from src.application.decision_intelligence.decision_status import DecisionStatus
from src.application.decision_intelligence.decision_confidence import DecisionConfidence
from src.application.decision_intelligence.decision_graph import DecisionGraph

class MockDependency:
    def __init__(self, src_id, tgt_id, rel="DEPENDS_ON", conf=1.0):
        self.source_decision_id = src_id
        self.target_decision_id = tgt_id
        self.relationship_type = rel
        self.confidence = conf

def _create_simple_decision(d_id, name):
    confidence = DecisionConfidence(
        score=0.8,
        evidence_coverage=0.8,
        historical_support=0.8,
        architectural_support=0.8,
        capability_support=0.8,
        artifact_agreement=0.0
    )
    return Decision(
        id=d_id,
        name=name,
        description="Desc",
        decision_type=DecisionType.TECHNOLOGY_ADOPTION,
        confidence=confidence,
        status=DecisionStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
        first_seen_commit="c1",
        last_seen_commit="c1",
        repository_id="repo-1",
        versions=[]
    )

def test_decision_graph_roots_leaves_topo():
    id_a = uuid.uuid4()
    id_b = uuid.uuid4()
    id_c = uuid.uuid4()
    
    dec_a = _create_simple_decision(id_a, "Decision A")
    dec_b = _create_simple_decision(id_b, "Decision B")
    dec_c = _create_simple_decision(id_c, "Decision C")
    
    # A -> B -> C
    dep1 = MockDependency(str(id_a), str(id_b))
    dep2 = MockDependency(str(id_b), str(id_c))
    
    graph = DecisionGraph([dec_a, dec_b, dec_c], [dep1, dep2])
    
    roots = graph.get_roots()
    assert len(roots) == 1
    assert roots[0].id == id_a
    
    leaves = graph.get_leaves()
    assert len(leaves) == 1
    assert leaves[0].id == id_c
    
    topo = graph.topological_sort()
    assert len(topo) == 3
    assert topo[0].id == id_a
    assert topo[1].id == id_b
    assert topo[2].id == id_c
