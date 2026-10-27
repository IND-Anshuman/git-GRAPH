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
        available: set[str] | None = None,
    ) -> "ArchitectureConfidence":
        """Weighted average of the components that were actually measured.

        ``available`` names the measured components (``topology``,
        ``dependency``, ``flow``, ``capability``, ``ownership``,
        ``historical``, ``evidence``). Unmeasured ones are excluded and the
        remaining weights renormalised, so a missing signal neither inflates
        nor deflates the score. ``None`` means every component was measured.
        """
        weights = {
            "topology": 0.25,
            "dependency": 0.2,
            "flow": 0.15,
            "capability": 0.15,
            "ownership": 0.1,
            "historical": 0.1,
            "evidence": 0.05,
        }

        values = {
            "topology": topology_match,
            "dependency": dependency_match,
            "flow": flow_match,
            "capability": capability_match,
            "ownership": ownership_match,
            "historical": historical_match,
            "evidence": evidence_coverage,
        }
        used = set(weights) if available is None else set(available) & set(weights)
        total_weight = sum(weights[k] for k in used)
        score = sum(values[k] * weights[k] for k in used) / total_weight if total_weight else 0.0

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
