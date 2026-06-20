import uuid
from datetime import datetime, timezone, timedelta
from src.application.decision_intelligence.decision import Decision
from src.application.decision_intelligence.decision_type import DecisionType
from src.application.decision_intelligence.decision_status import DecisionStatus
from src.application.decision_intelligence.decision_confidence import DecisionConfidence
from src.application.decision_intelligence.decision_version import DecisionVersion
from src.application.decision_intelligence.decision_evidence import DecisionEvidence
from src.application.decision_intelligence.decision_fitness_engine import DecisionFitnessEngine

def test_evaluate_fitness_simple():
    engine = DecisionFitnessEngine()
    
    decision_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    birth = now - timedelta(days=365) # 1 year old -> longevity_score should be 365/730 = 0.5
    
    confidence = DecisionConfidence(
        score=0.8,
        evidence_coverage=0.8,
        historical_support=0.8,
        architectural_support=0.8,
        capability_support=0.8,
        artifact_agreement=0.0
    )
    
    versions = [
        DecisionVersion(decision_id=decision_id, version=1, commit_hash="h1", confidence=0.8, supporting_evidence=[], generated_at=birth),
        DecisionVersion(decision_id=decision_id, version=2, commit_hash="h2", confidence=0.8, supporting_evidence=[], generated_at=now)
    ]
    
    evidence = DecisionEvidence(
        supporting_commits=["c1", "c2"],
        supporting_documents=[],
        supporting_capabilities=[],
        supporting_architecture_changes=[],
        supporting_repository_events=[]
    )
    
    decision = Decision(
        id=decision_id,
        name="Adopt PostgreSQL",
        description="We adopt postgresql",
        decision_type=DecisionType.TECHNOLOGY_ADOPTION,
        confidence=confidence,
        status=DecisionStatus.ACTIVE,
        created_at=birth,
        first_seen_commit="c1",
        last_seen_commit="c2",
        repository_id="test-repo",
        versions=versions,
        supporting_evidence=evidence,
        affected_capabilities=["cap1"],
        affected_architectures=["arch1"],
        affected_services=["srv1"]
    )
    
    fitness = engine.evaluate_fitness(decision, reference_date=now)
    
    assert fitness.decision_id == decision_id
    # Longevity: 365 days / 730 = 0.5
    assert abs(fitness.longevity_score - 0.5) < 0.05
    # Churn: 2 versions -> stability = 1.0 - (2-1)/5 = 0.8
    assert abs(fitness.stability_score - 0.8) < 0.05
    assert fitness.overall_fitness > 0.0
