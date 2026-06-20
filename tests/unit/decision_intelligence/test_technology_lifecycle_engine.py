import uuid
from datetime import datetime, timezone, timedelta
from src.application.decision_intelligence.decision import Decision
from src.application.decision_intelligence.decision_type import DecisionType
from src.application.decision_intelligence.decision_status import DecisionStatus
from src.application.decision_intelligence.decision_confidence import DecisionConfidence
from src.application.decision_intelligence.decision_version import DecisionVersion
from src.application.decision_intelligence.decision_evidence import DecisionEvidence
from src.application.decision_intelligence.technology_lifecycle_engine import TechnologyLifecycleEngine

def test_detect_lifecycles_active_and_retired():
    engine = TechnologyLifecycleEngine()
    
    # 1. Create technology adoption (active)
    dec_a_id = uuid.uuid4()
    confidence = DecisionConfidence(
        score=0.8,
        evidence_coverage=0.8,
        historical_support=0.8,
        architectural_support=0.8,
        capability_support=0.8,
        artifact_agreement=0.0
    )
    dec_a = Decision(
        id=dec_a_id,
        name="Adopt PostgreSQL",
        description="Adopt postgresql",
        decision_type=DecisionType.TECHNOLOGY_ADOPTION,
        confidence=confidence,
        status=DecisionStatus.ACTIVE,
        created_at=datetime.now(timezone.utc) - timedelta(days=20),
        first_seen_commit="c1",
        last_seen_commit="c1",
        repository_id="repo-1",
        versions=[DecisionVersion(decision_id=dec_a_id, version=1, commit_hash="c1", confidence=0.8, supporting_evidence=[], generated_at=datetime.now(timezone.utc) - timedelta(days=20))]
    )
    
    # 2. Create technology adoption + removal (retired)
    dec_b_id = uuid.uuid4()
    dec_b = Decision(
        id=dec_b_id,
        name="Adopt Django",
        description="Adopt django",
        decision_type=DecisionType.TECHNOLOGY_ADOPTION,
        confidence=confidence,
        status=DecisionStatus.SUPERSEDED,
        created_at=datetime.now(timezone.utc) - timedelta(days=50),
        first_seen_commit="c0",
        last_seen_commit="c0",
        repository_id="repo-1",
        versions=[DecisionVersion(decision_id=dec_b_id, version=1, commit_hash="c0", confidence=0.8, supporting_evidence=[], generated_at=datetime.now(timezone.utc) - timedelta(days=50))]
    )
    
    dec_b_remove_id = uuid.uuid4()
    dec_b_remove = Decision(
        id=dec_b_remove_id,
        name="Remove Django",
        description="Remove django in favor of FastAPI",
        decision_type=DecisionType.TECHNOLOGY_REMOVAL,
        confidence=confidence,
        status=DecisionStatus.ACTIVE,
        created_at=datetime.now(timezone.utc) - timedelta(days=10),
        first_seen_commit="c3",
        last_seen_commit="c3",
        repository_id="repo-1",
        versions=[DecisionVersion(decision_id=dec_b_remove_id, version=1, commit_hash="c3", confidence=0.8, supporting_evidence=[], generated_at=datetime.now(timezone.utc) - timedelta(days=10))]
    )
    
    lifecycles = engine.detect_lifecycles([dec_a, dec_b, dec_b_remove])
    
    assert len(lifecycles) == 2
    
    l_postgres = next(l for l in lifecycles if l.technology_key == "postgresql")
    assert l_postgres.status == "ACTIVE"
    assert l_postgres.removal_decision_id is None
    
    l_django = next(l for l in lifecycles if l.technology_key == "django")
    assert l_django.status == "RETIRED"
    assert l_django.removal_decision_id == dec_b_remove_id
    assert l_django.lifespan_days == 40
