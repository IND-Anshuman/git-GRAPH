"""Value object representing a decomposed confidence score for a logic detection."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceBreakdown:
    """
    Immutable value object that breaks down an overall detection confidence
    into its contributing signal categories.

    Weights applied during overall computation:
        AST         → 0.30
        Dependency  → 0.25
        Data Flow   → 0.20
        Pattern     → 0.15
        Structural  → 0.10
    """

    overall_confidence: float
    """Weighted aggregate confidence in [0.0, 1.0]."""

    ast_confidence: float
    """Confidence contribution from AST call/import evidence."""

    dependency_confidence: float
    """Confidence contribution from package-level dependency evidence."""

    data_flow_confidence: float
    """Confidence contribution from data-flow path evidence."""

    pattern_confidence: float
    """Confidence contribution from composite pattern rule evidence."""

    structural_confidence: float
    """Confidence contribution from structural shape evidence."""

    evidence_count: int
    """Total number of evidence items that contributed to this score."""

    def __post_init__(self) -> None:
        """Validate that all float fields lie within [0.0, 1.0]."""
        float_fields = {
            "overall_confidence": self.overall_confidence,
            "ast_confidence": self.ast_confidence,
            "dependency_confidence": self.dependency_confidence,
            "data_flow_confidence": self.data_flow_confidence,
            "pattern_confidence": self.pattern_confidence,
            "structural_confidence": self.structural_confidence,
        }
        for name, val in float_fields.items():
            if not (0.0 <= val <= 1.0):
                raise ValueError(
                    f"ConfidenceBreakdown.{name} must be in [0.0, 1.0], got {val}"
                )

    @classmethod
    def compute(
        cls,
        ast: float,
        dependency: float,
        data_flow: float,
        pattern: float,
        structural: float,
        evidence_count: int,
    ) -> "ConfidenceBreakdown":
        """
        Compute a ConfidenceBreakdown from individual signal scores.

        Overall confidence is calculated as:
            0.30 * ast + 0.25 * dependency + 0.20 * data_flow
            + 0.15 * pattern + 0.10 * structural

        The result is clamped to [0.05, 1.0] to avoid zero-confidence detections
        that had any evidence at all.

        Args:
            ast: AST evidence confidence [0.0, 1.0].
            dependency: Dependency evidence confidence [0.0, 1.0].
            data_flow: Data-flow evidence confidence [0.0, 1.0].
            pattern: Pattern rule evidence confidence [0.0, 1.0].
            structural: Structural shape evidence confidence [0.0, 1.0].
            evidence_count: Total number of evidence items.

        Returns:
            A fully computed ConfidenceBreakdown instance.
        """
        raw_overall = (
            0.30 * ast
            + 0.25 * dependency
            + 0.20 * data_flow
            + 0.15 * pattern
            + 0.10 * structural
        )
        overall = max(0.05, min(1.0, raw_overall))
        return cls(
            overall_confidence=overall,
            ast_confidence=ast,
            dependency_confidence=dependency,
            data_flow_confidence=data_flow,
            pattern_confidence=pattern,
            structural_confidence=structural,
            evidence_count=evidence_count,
        )

    def to_dict(self) -> dict:
        """Serialize to a plain dict suitable for JSONB storage."""
        return {
            "overall_confidence": self.overall_confidence,
            "ast_confidence": self.ast_confidence,
            "dependency_confidence": self.dependency_confidence,
            "data_flow_confidence": self.data_flow_confidence,
            "pattern_confidence": self.pattern_confidence,
            "structural_confidence": self.structural_confidence,
            "evidence_count": self.evidence_count,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ConfidenceBreakdown":
        """Deserialize from a plain dict (e.g., loaded from JSONB)."""
        return cls(
            overall_confidence=float(d["overall_confidence"]),
            ast_confidence=float(d["ast_confidence"]),
            dependency_confidence=float(d["dependency_confidence"]),
            data_flow_confidence=float(d["data_flow_confidence"]),
            pattern_confidence=float(d["pattern_confidence"]),
            structural_confidence=float(d["structural_confidence"]),
            evidence_count=int(d["evidence_count"]),
        )
