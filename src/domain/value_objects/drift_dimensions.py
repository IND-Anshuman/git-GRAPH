"""Value object representing multi-dimensional drift scores between two logic versions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DriftDimensions:
    """
    Immutable value object capturing how much each behavioral dimension drifted
    between two logic versions.

    Weights applied during overall drift computation:
        Structural   → 0.30
        Dependency   → 0.25
        API Surface  → 0.15
        Control Flow → 0.15
        Ontology     → 0.10
        Security     → 0.05
    """

    structural_drift: float
    """Degree of change in the AST/structural shape of the implementation."""

    dependency_drift: float
    """Degree of change in external library and import usage."""

    api_surface_drift: float
    """Degree of change in the public API surface (signatures, parameter names)."""

    control_flow_drift: float
    """Degree of change in control-flow paths (branches, loops, exception handling)."""

    ontology_drift: float
    """Degree of change in the semantic classification (ontology node)."""

    security_drift: float
    """Degree of change in security-sensitive properties (e.g., hash algorithm swapped)."""

    def __post_init__(self) -> None:
        """Validate that all drift dimensions are in [0.0, 1.0]."""
        dimension_fields = {
            "structural_drift": self.structural_drift,
            "dependency_drift": self.dependency_drift,
            "api_surface_drift": self.api_surface_drift,
            "control_flow_drift": self.control_flow_drift,
            "ontology_drift": self.ontology_drift,
            "security_drift": self.security_drift,
        }
        for name, val in dimension_fields.items():
            if not (0.0 <= val <= 1.0):
                raise ValueError(
                    f"DriftDimensions.{name} must be in [0.0, 1.0], got {val}"
                )

    def compute_overall(self) -> float:
        """
        Compute the overall drift score as a weighted average of all dimensions.

        Returns:
            A float in [0.0, 1.0] representing aggregate drift magnitude.
        """
        return (
            0.30 * self.structural_drift
            + 0.25 * self.dependency_drift
            + 0.15 * self.api_surface_drift
            + 0.15 * self.control_flow_drift
            + 0.10 * self.ontology_drift
            + 0.05 * self.security_drift
        )

    def to_dict(self) -> dict:
        """Serialize to a plain dict suitable for JSONB storage."""
        return {
            "structural_drift": self.structural_drift,
            "dependency_drift": self.dependency_drift,
            "api_surface_drift": self.api_surface_drift,
            "control_flow_drift": self.control_flow_drift,
            "ontology_drift": self.ontology_drift,
            "security_drift": self.security_drift,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "DriftDimensions":
        """Deserialize from a plain dict (e.g., loaded from JSONB)."""
        return cls(
            structural_drift=float(d["structural_drift"]),
            dependency_drift=float(d["dependency_drift"]),
            api_surface_drift=float(d["api_surface_drift"]),
            control_flow_drift=float(d["control_flow_drift"]),
            ontology_drift=float(d["ontology_drift"]),
            security_drift=float(d["security_drift"]),
        )
