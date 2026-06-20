import uuid
from datetime import datetime, timezone, timedelta
from src.application.decision_intelligence.decision import Decision
from src.application.decision_intelligence.decision_type import DecisionType
from src.application.decision_intelligence.decision_status import DecisionStatus
from src.application.decision_intelligence.decision_confidence import DecisionConfidence
from src.application.decision_intelligence.decision_version import DecisionVersion
from src.application.decision_intelligence.decision_evidence import DecisionEvidence
from src.application.decision_intelligence.decision_evolution_engine import DecisionEvolutionEngine

def test_build_timeline_and_detect_patterns():
    engine = DecisionEvolutionEngine()
    
    now = datetime.now(timezone.utc)
    
    dec_a_id = uuid.uuid4()
    confidence_a = DecisionConfidence(
        score=0.8,
        evidence_coverage=0.8,
        historical_support=0.8,
        architectural_support=0.8,
        capability_support=0.8,
        artifact_agreement=0.0
    )
    versions_a = [
        DecisionVersion(decision_id=dec_a_id, version=1, commit_hash="c1", confidence=0.8, supporting_evidence=[], generated_at=now - timedelta(days=10))
    ]
    dec_a = Decision(
        id=dec_a_id,
        name="Adopt Django",
        description="First framework choice",
        decision_type=DecisionType.TECHNOLOGY_ADOPTION,
        confidence=confidence_a,
        status=DecisionStatus.SUPERSEDED,
        created_at=now - timedelta(days=10),
        first_seen_commit="c1",
        last_seen_commit="c1",
        repository_id="repo-1",
        versions=versions_a,
        supporting_evidence=DecisionEvidence(supporting_commits=["c1"])
    )
    
    dec_b_id = uuid.uuid4()
    confidence_b = DecisionConfidence(
        score=0.9,
        evidence_coverage=0.9,
        historical_support=0.9,
        architectural_support=0.9,
        capability_support=0.9,
        artifact_agreement=0.0
    )
    versions_b = [
        DecisionVersion(decision_id=dec_b_id, version=1, commit_hash="c2", confidence=0.9, supporting_evidence=[], generated_at=now - timedelta(days=5))
    ]
    dec_b = Decision(
        id=dec_b_id,
        name="Adopt FastAPI",
        description="Replacing Django with FastAPI",
        decision_type=DecisionType.TECHNOLOGY_ADOPTION,
        confidence=confidence_b,
        status=DecisionStatus.ACTIVE,
        created_at=now - timedelta(days=5),
        first_seen_commit="c2",
        last_seen_commit="c2",
        repository_id="repo-1",
        versions=versions_b,
        supporting_evidence=DecisionEvidence(supporting_commits=["c2"])
    )
    
    decisions = [dec_a, dec_b]
    timeline = engine.build_timeline(decisions)
    
    assert timeline.repository_id == "repo-1"
    assert len(timeline.snapshots) == 2
    assert timeline.first_commit == "c1"
    assert timeline.last_commit == "c2"
    
    patterns = engine.detect_evolution_patterns(timeline, decisions)
    assert len(patterns["supersessions"]) == 1
    assert patterns["supersessions"][0]["superseded_id"] == str(dec_a_id)
    assert patterns["supersessions"][0]["replacement_id"] == str(dec_b_id)
