"""Domain entities for human-readable behavior explanations and per-rule verdicts."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.domain.value_objects.confidence_breakdown import ConfidenceBreakdown


@dataclass(frozen=True)
class RuleVerdict:
    """
    Immutable record of a single pattern rule's evaluation outcome within a
    BehaviorExplanation.

    Each rule contributes independently to the overall explanation, and its
    verdict (passed/failed) plus its weighted contribution are stored here for
    full auditability.
    """

    rule_id: str
    """Unique identifier of the pattern rule that was evaluated."""

    rule_description: str
    """Human-readable description of what this rule checks."""

    passed: bool
    """True if this rule's criteria were satisfied by the detected logic."""

    contribution: float
    """Fractional confidence contribution from this rule (typically in [0.0, 1.0])."""

    evidence_ref: uuid.UUID | None = None
    """Optional reference to the LogicEvidence record that triggered this verdict."""

    def to_dict(self) -> dict:
        """Serialize to a plain dict suitable for JSONB storage."""
        return {
            "rule_id": self.rule_id,
            "rule_description": self.rule_description,
            "passed": self.passed,
            "contribution": self.contribution,
            "evidence_ref": str(self.evidence_ref) if self.evidence_ref else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RuleVerdict":
        """Deserialize from a plain dict (e.g., loaded from JSONB)."""
        evidence_ref = (
            uuid.UUID(d["evidence_ref"]) if d.get("evidence_ref") else None
        )
        return cls(
            rule_id=d["rule_id"],
            rule_description=d["rule_description"],
            passed=bool(d["passed"]),
            contribution=float(d["contribution"]),
            evidence_ref=evidence_ref,
        )


@dataclass
class BehaviorExplanation:
    """
    A structured, human-readable explanation of why a particular LogicVersion was
    classified as exhibiting a given named behavior.

    Explanations are generated after detection and can be marked stale when the
    underlying pattern definitions change, triggering regeneration.
    """

    id: uuid.UUID
    """Unique identifier for this explanation record."""

    logic_version_id: uuid.UUID
    """The LogicVersion this explanation is attached to."""

    behavior_name: str
    """Display name of the detected behavior (e.g., 'bcrypt password verification')."""

    ontology_path: str
    """Dot-path location in the ontology (e.g., 'security.authentication.hash_comparison')."""

    overall_confidence: float
    """Aggregate confidence score for this behavior classification."""

    confidence_breakdown: ConfidenceBreakdown
    """Detailed per-signal confidence breakdown."""

    matched_pattern_ids: list[str] = field(default_factory=list)
    """List of pattern IDs (from BehaviorPattern) that contributed to this detection."""

    evidence_summary: str = ""
    """Concise human-readable summary of the strongest evidence items."""

    rule_verdicts: list[RuleVerdict] = field(default_factory=list)
    """Per-rule evaluation outcomes, ordered by contribution descending."""

    is_stale: bool = False
    """True when the underlying pattern definition has changed since generation."""

    generated_at: datetime = field(default_factory=datetime.utcnow)
    """UTC timestamp when this explanation was produced."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Arbitrary extensible metadata."""
