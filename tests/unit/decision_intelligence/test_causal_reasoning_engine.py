import uuid
from datetime import datetime, timezone
from src.application.decision_intelligence.decision import Decision
from src.application.decision_intelligence.decision_type import DecisionType
from src.application.decision_intelligence.decision_status import DecisionStatus
from src.application.decision_intelligence.decision_confidence import DecisionConfidence
from src.application.decision_intelligence.decision_version import DecisionVersion
from src.application.decision_intelligence.decision_evidence import DecisionEvidence
from src.application.decision_intelligence.intent_type import IntentType
from src.application.decision_intelligence.causal_reasoning_engine import CausalReasoningEngine

def test_infer_causes_simple():
    engine = CausalReasoningEngine()
    
    dec_id = uuid.uuid4()
    confidence = DecisionConfidence(
        score=0.8,
        evidence_coverage=0.8,
        historical_support=0.8,
        architectural_support=0.8,
        capability_support=0.8,
        artifact_agreement=0.0
    )
    decision = Decision(
        id=dec_id,
        name="Adopt OpenAI API",
        description="Integrate LLMs",
        decision_type=DecisionType.AI_ADOPTION,
        confidence=confidence,
        status=DecisionStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
        first_seen_commit="c1",
        last_seen_commit="c1",
        repository_id="repo-1",
        versions=[DecisionVersion(decision_id=dec_id, version=1, commit_hash="c1", confidence=0.8, supporting_evidence=[], generated_at=datetime.now(timezone.utc))],
        supporting_evidence=DecisionEvidence(supporting_commits=["c1"])
    )
    
    chains = engine.infer_causes([decision], [])
    
    assert len(chains) == 1
    chain = chains[0]
    assert chain.root_cause_id is not None
    assert len(chain.relationships) == 1
    rel = chain.relationships[0]
    assert rel.relationship_type == "MOTIVATES"
    assert rel.cause_id == chain.root_cause_id
    assert rel.effect_id == decision.id
