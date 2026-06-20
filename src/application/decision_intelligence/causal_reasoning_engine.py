from typing import List, Dict, Any
from .decision import Decision
from .intent import Intent
from .causal_chain import CausalChain
from .causal_relationship import CausalRelationship
import uuid

class CausalReasoningEngine:
    def infer_causes(self, decisions: List[Decision], intents: List[Intent]) -> List[CausalChain]:
        chains = []
        # Simple rule-based causal linking: Intent -> Decision
        for intent in intents:
            relationships = []
            for d_id in intent.supporting_decisions:
                rel = CausalRelationship(
                    cause_id=intent.id,
                    effect_id=uuid.UUID(d_id) if isinstance(d_id, str) else d_id,
                    cause_label=f"Intent: {intent.name}",
                    effect_label=f"Decision: {d_id}",
                    relationship_type="MOTIVATES",
                    confidence=0.7,
                    evidence=[]
                )
                relationships.append(rel)
                
            if relationships:
                chain = CausalChain(
                    chain_id=uuid.uuid4(),
                    repository_id=intent.repository_id,
                    root_cause_id=intent.id,
                    relationships=relationships,
                    summary=f"Chain rooted at {intent.name}",
                    confidence=0.7,
                    generated_at=None
                )
                chains.append(chain)
        return chains
