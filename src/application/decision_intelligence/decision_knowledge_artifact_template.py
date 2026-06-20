from dataclasses import dataclass, field

@dataclass
class DecisionKnowledgeArtifactTemplate:
    decision: str
    confidence: float
    supporting_evidence: list[str] = field(default_factory=list)
    affected_capabilities: list[str] = field(default_factory=list)
    affected_architecture: list[str] = field(default_factory=list)
    causal_chain: list[str] = field(default_factory=list)
    alternative_hypotheses: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "confidence": self.confidence,
            "supporting_evidence": self.supporting_evidence,
            "affected_capabilities": self.affected_capabilities,
            "affected_architecture": self.affected_architecture,
            "causal_chain": self.causal_chain,
            "alternative_hypotheses": self.alternative_hypotheses
        }
