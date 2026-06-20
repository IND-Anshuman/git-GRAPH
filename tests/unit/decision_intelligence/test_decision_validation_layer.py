import uuid
from datetime import datetime, timezone
from src.application.decision_intelligence.decision import Decision
from src.application.decision_intelligence.decision_type import DecisionType
from src.application.decision_intelligence.decision_status import DecisionStatus
from src.application.decision_intelligence.decision_confidence import DecisionConfidence
from src.application.decision_intelligence.decision_version import DecisionVersion
from src.application.decision_intelligence.decision_evidence import DecisionEvidence
from src.application.decision_intelligence.decision_validation_layer import DecisionValidationLayer

def _create_test_decision(
    name="Test Decision",
    description="Valid Description",
    confidence_score=0.8,
    status=DecisionStatus.ACTIVE,
    version_count=1,
    has_evidence=True
):
    decision_id = uuid.uuid4()
    confidence = DecisionConfidence(
        score=confidence_score,
        evidence_coverage=0.8,
        historical_support=0.8,
        architectural_support=0.8,
        capability_support=0.8,
        artifact_agreement=0.0
    )
    versions = [
        DecisionVersion(
            decision_id=decision_id,
            version=i,
            commit_hash=f"hash{i}",
            confidence=confidence_score,
            supporting_evidence=[],
            generated_at=datetime.now(timezone.utc)
        )
        for i in range(1, version_count + 1)
    ]
    
    evidence = DecisionEvidence(
        supporting_commits=["c1"] if has_evidence else [],
        supporting_documents=[],
        supporting_capabilities=[],
        supporting_architecture_changes=[],
        supporting_repository_events=[]
    )
    
    return Decision(
        id=decision_id,
        name=name,
        description=description,
        decision_type=DecisionType.TECHNOLOGY_ADOPTION,
        confidence=confidence,
        status=status,
        created_at=datetime.now(timezone.utc),
        first_seen_commit="c1",
        last_seen_commit="c1",
        repository_id="repo-1",
        versions=versions,
        supporting_evidence=evidence
    )

def test_validation_layer_valid():
    validator = DecisionValidationLayer()
    decision = _create_test_decision()
    valid, rejected = validator.validate([decision])
    assert len(valid) == 1
    assert len(rejected) == 0

def test_validation_layer_low_confidence():
    validator = DecisionValidationLayer()
    decision = _create_test_decision(confidence_score=0.1)
    valid, rejected = validator.validate([decision])
    assert len(valid) == 0
    assert len(rejected) == 1
    assert "confidence 0.100 < threshold" in rejected[0].reasons[0]

def test_validation_layer_missing_evidence():
    validator = DecisionValidationLayer()
    decision = _create_test_decision(has_evidence=False)
    valid, rejected = validator.validate([decision])
    assert len(valid) == 0
    assert len(rejected) == 1
    assert "no provenanced evidence attached" in rejected[0].reasons[0]

def test_validation_layer_empty_fields():
    validator = DecisionValidationLayer()
    decision = _create_test_decision(name="", description=" ")
    valid, rejected = validator.validate([decision])
    assert len(valid) == 0
    assert len(rejected) == 1
    assert any("decision name is empty" in r for r in rejected[0].reasons)
    assert any("decision description is empty" in r for r in rejected[0].reasons)

def test_validation_layer_invalid_transitions():
    validator = DecisionValidationLayer()
    # Newborn decision (v1) with SUPERSEDED status
    decision_new_superseded = _create_test_decision(status=DecisionStatus.SUPERSEDED, version_count=1)
    valid, rejected = validator.validate([decision_new_superseded])
    assert len(valid) == 0
    assert len(rejected) == 1
    
    # Evolved SUPERSEDED decision with version_count > 2
    decision_evolved_superseded = _create_test_decision(status=DecisionStatus.SUPERSEDED, version_count=3)
    valid, rejected = validator.validate([decision_evolved_superseded])
    assert len(valid) == 0
    assert len(rejected) == 1
