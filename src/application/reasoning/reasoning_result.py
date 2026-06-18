"""
Phase 7A — ReasoningResult

The rich, auditable output of one reasoning execution.

Every field is required.  The result carries:
  * A unique ``execution_id`` for deduplication and caching.
  * The original ``question`` as asked.
  * A natural-language ``answer``.
  * A ``confidence`` object with level tier and numeric score.
  * A full ``reasoning_chain`` step trace.
  * An ``provenance_graph`` DAG mapping evidence → conclusion.
  * Raw ``evidence`` list (all validated nodes).
  * The ``selected_hypothesis`` chosen as the best explanation.
  * ``alternative_hypotheses`` for transparency.
  * ``limitations`` documenting known gaps so consumers don't over-trust.
  * ``generated_at`` UTC timestamp.
  * ``source_ids`` — flat list of all evidence source IDs used.
  * A ``snapshot`` of the graph state when the question was answered.

Schema changes
--------------
Adding new optional fields in Phase 7B/7C does NOT break existing callers
because Python dataclasses with defaults are backward-compatible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.application.reasoning.reasoning_confidence import ReasoningConfidence
from src.application.reasoning.reasoning_chain import ReasoningChain
from src.application.reasoning.evidence_provenance_graph import EvidenceProvenanceGraph
from src.application.reasoning.reasoning_evidence import ReasoningEvidence
from src.application.reasoning.reasoning_hypothesis import ReasoningHypothesis
from src.application.reasoning.reasoning_limitations import ReasoningLimitation
from src.application.reasoning.reasoning_snapshot import ReasoningSnapshot


@dataclass
class ReasoningResult:
    """Fully auditable output of a Phase 7A reasoning execution.

    All fields are populated before the result leaves the engine; none are
    optional (except ``selected_hypothesis`` which may be None for degenerate
    queries with zero evidence).
    """

    # ── Identity / traceability ────────────────────────────────────────────────
    execution_id: str
    """UUID string uniquely identifying this reasoning run."""

    question: str
    """The original user question, verbatim."""

    # ── Primary output ─────────────────────────────────────────────────────────
    answer: str
    """Natural-language answer synthesised from the selected hypothesis."""

    confidence: ReasoningConfidence
    """Weighted evidence coverage score plus human-readable tier."""

    # ── Audit trail ────────────────────────────────────────────────────────────
    reasoning_chain: ReasoningChain
    """Step-by-step trace of every engine stage in the pipeline."""

    provenance_graph: EvidenceProvenanceGraph
    """DAG tracking which evidence nodes were used to reach the conclusion."""

    # ── Evidence ───────────────────────────────────────────────────────────────
    evidence: list[ReasoningEvidence]
    """All validated evidence nodes consumed during this execution."""

    # ── Hypothesis ─────────────────────────────────────────────────────────────
    selected_hypothesis: ReasoningHypothesis | None
    """Best-scoring candidate explanation (None if no evidence found)."""

    alternative_hypotheses: list[ReasoningHypothesis] = field(default_factory=list)
    """Competing explanations retained for transparency."""

    # ── Limitations ────────────────────────────────────────────────────────────
    limitations: list[ReasoningLimitation] = field(default_factory=list)
    """Explicit list of gaps / missing data that affect result reliability."""

    # ── Temporal metadata ──────────────────────────────────────────────────────
    generated_at: datetime = field(default_factory=datetime.utcnow)
    """UTC timestamp when this result was produced."""

    source_ids: list[str] = field(default_factory=list)
    """Flat list of all evidence source_ids used in this result."""

    snapshot: ReasoningSnapshot | None = None
    """Graph state snapshot at the time of execution."""

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary of the full result."""
        return {
            "execution_id": self.execution_id,
            "question": self.question,
            "answer": self.answer,
            "confidence": {
                "score": self.confidence.score,
                "level": self.confidence.level.value,
                "rationale": self.confidence.rationale,
            },
            "reasoning_chain": self.reasoning_chain.to_dict(),
            "provenance_graph": self.provenance_graph.to_dict(),
            "evidence": [e.to_dict() for e in self.evidence],
            "selected_hypothesis": (
                self.selected_hypothesis.to_dict()
                if self.selected_hypothesis
                else None
            ),
            "alternative_hypotheses": [h.to_dict() for h in self.alternative_hypotheses],
            "limitations": [lim.to_dict() for lim in self.limitations],
            "generated_at": self.generated_at.isoformat(),
            "source_ids": self.source_ids,
            "snapshot": self.snapshot.to_dict() if self.snapshot else None,
        }
