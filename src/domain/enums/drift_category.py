"""Enum defining drift severity categories based on computed drift scores."""

from enum import Enum


class DriftCategory(str, Enum):
    """Categorical label for the degree of behavioral drift detected between two logic versions."""

    TRIVIAL = "TRIVIAL"
    """Drift score in range [0.00, 0.10): negligible change."""

    MINOR = "MINOR"
    """Drift score in range [0.10, 0.30): small but notable change."""

    SIGNIFICANT = "SIGNIFICANT"
    """Drift score in range [0.30, 0.60): meaningful behavioral change."""

    MAJOR = "MAJOR"
    """Drift score in range [0.60, 0.85): substantial behavioral change."""

    COMPLETE = "COMPLETE"
    """Drift score in range [0.85, 1.00]: near-total replacement of behavior."""
