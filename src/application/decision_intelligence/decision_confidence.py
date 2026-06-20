from dataclasses import dataclass

@dataclass(frozen=True)
class DecisionConfidence:
    evidence_coverage: float
    historical_support: float
    architectural_support: float
    capability_support: float
    artifact_agreement: float
    score: float

    @classmethod
    def compute(cls, evidence_coverage: float, historical_support: float,
                architectural_support: float, capability_support: float,
                artifact_agreement: float) -> 'DecisionConfidence':
        score = (
            0.30 * evidence_coverage +
            0.25 * historical_support +
            0.20 * architectural_support +
            0.15 * capability_support +
            0.10 * artifact_agreement
        )
        return cls(
            evidence_coverage=evidence_coverage,
            historical_support=historical_support,
            architectural_support=architectural_support,
            capability_support=capability_support,
            artifact_agreement=artifact_agreement,
            score=score
        )
