"""Domain model representing the confidence breakdown of an architecture detection."""

from dataclasses import dataclass

@dataclass(frozen=True)
class ArchitectureConfidence:
    """Confidence scores across various architectural dimensions. All scores are in [0.0, 1.0]."""
    score: float
    topology_match: float
    dependency_match: float
    flow_match: float
    capability_match: float
    ownership_match: float
    historical_match: float
    evidence_coverage: float

    @classmethod
    def compute(
        cls,
        topology_match: float,
        dependency_match: float,
        flow_match: float,
        capability_match: float,
        ownership_match: float,
        historical_match: float,
        evidence_coverage: float,
    ) -> "ArchitectureConfidence":
        """Compute the overall score using weighted averages of components."""
        weights = {
            "topology": 0.25,
            "dependency": 0.2,
            "flow": 0.15,
            "capability": 0.15,
            "ownership": 0.1,
            "historical": 0.1,
            "evidence": 0.05,
        }
        
        score = (
            topology_match * weights["topology"] +
            dependency_match * weights["dependency"] +
            flow_match * weights["flow"] +
            capability_match * weights["capability"] +
            ownership_match * weights["ownership"] +
            historical_match * weights["historical"] +
            evidence_coverage * weights["evidence"]
        )

        return cls(
            score=max(0.0, min(1.0, score)),
            topology_match=max(0.0, min(1.0, topology_match)),
            dependency_match=max(0.0, min(1.0, dependency_match)),
            flow_match=max(0.0, min(1.0, flow_match)),
            capability_match=max(0.0, min(1.0, capability_match)),
            ownership_match=max(0.0, min(1.0, ownership_match)),
            historical_match=max(0.0, min(1.0, historical_match)),
            evidence_coverage=max(0.0, min(1.0, evidence_coverage)),
        )
