from typing import List, Dict, Any
from .decision import Decision
from .decision_type import DecisionType
from .decision_status import DecisionStatus
from .decision_confidence import DecisionConfidence
from .decision_evidence import DecisionEvidence
import uuid
from datetime import datetime, timezone

class DecisionDiscoveryEngine:
    def __init__(self, decision_registry, intent_registry):
        self.decision_registry = decision_registry
        self.intent_registry = intent_registry
        
    def discover_from_memory(self, memory, adr_graphs) -> List[Decision]:
        decisions = []
        
        # Simple mock discovery logic based on memory events
        for intro in memory.technology_introductions:
            decision = Decision(
                id=uuid.uuid4(),
                name=f"Adopted technology in {intro}",
                description="Discovered from dependency change",
                decision_type=DecisionType.TECHNOLOGY_ADOPTION,
                confidence=DecisionConfidence.compute(0.8, 0.5, 0.5, 0.0, 0.0),
                status=DecisionStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
                first_seen_commit=intro,
                last_seen_commit=intro,
                repository_id=memory.repository_id,
                supporting_evidence=DecisionEvidence(supporting_commits=[intro])
            )
            decisions.append(decision)
            
        return decisions
