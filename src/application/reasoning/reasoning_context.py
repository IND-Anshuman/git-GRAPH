"""
Phase 7A — ReasoningContext

The single carry-bag that flows through the entire reasoning pipeline.
Every engine in the pipeline reads from and writes back to the context,
eliminating the need for many-argument function signatures.

Pipeline flow::

    Evidence Collection
           ↓
    ReasoningContext (populated)
           ↓
    Evidence Expansion
           ↓
    Evidence Validation
           ↓
    IReasoningStrategy.execute(context)
           ↓
    Hypothesis Generation
           ↓
    Hypothesis Scoring
           ↓
    ReasoningResult (built from context)

Design notes
------------
* The context is intentionally *not* frozen — engines mutate it in sequence.
* ``snapshot`` is set once at context creation and never mutated.
* ``chain`` accumulates steps from every pipeline stage.
* All evidence lists start empty and are populated by the collection /
  expansion engines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from src.application.reasoning.reasoning_question_type import ReasoningQuestionType
from src.application.reasoning.reasoning_snapshot import ReasoningSnapshot
from src.application.reasoning.reasoning_chain import ReasoningChain
from src.application.reasoning.reasoning_evidence import ReasoningEvidence
from src.application.reasoning.reasoning_hypothesis import ReasoningHypothesis
from src.application.reasoning.reasoning_confidence import ReasoningConfidence


@dataclass
class ReasoningContext:
    """Mutable pipeline carry-bag for one reasoning execution.

    Attributes:
        execution_id:       Unique run identifier (UUID string).
        repository_id:      Target repository UUID string.
        query:              Original user question text.
        question_type:      Classified question type (from QueryPlanner).
        snapshot:           Immutable graph state at time of execution.
        chain:              Step trace accumulator.

        entities:           Collected entity records (dicts from the DB).
        relationships:      Collected relationship records.
        concepts:           Collected concept records.
        capabilities:       Collected capability records.
        flows:              Collected flow records.
        artifacts:          Collected artifact records.

        expanded_evidence:  Evidence nodes after multi-hop expansion.
        validated_evidence: Evidence nodes confirmed by validation layer.

        hypotheses:         Candidate explanations generated.
        selected_hypothesis: Best-scoring hypothesis (set by scoring engine).
        confidence:         Overall confidence score (set by scoring engine).

        metadata:           Arbitrary key-value bag for engine-specific data.
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    execution_id: str
    repository_id: str
    query: str
    question_type: ReasoningQuestionType
    snapshot: ReasoningSnapshot

    # ── Step trace ────────────────────────────────────────────────────────────
    chain: ReasoningChain = field(default_factory=lambda: ReasoningChain(execution_id=""))

    # ── Raw collected data (populated by EvidenceCollectionEngine) ────────────
    entities: list[dict[str, Any]] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    concepts: list[dict[str, Any]] = field(default_factory=list)
    capabilities: list[dict[str, Any]] = field(default_factory=list)
    flows: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)

    # ── Processed evidence ────────────────────────────────────────────────────
    expanded_evidence: list[ReasoningEvidence] = field(default_factory=list)
    validated_evidence: list[ReasoningEvidence] = field(default_factory=list)

    # ── Hypothesis pipeline state ─────────────────────────────────────────────
    hypotheses: list[ReasoningHypothesis] = field(default_factory=list)
    selected_hypothesis: Optional[ReasoningHypothesis] = None
    confidence: Optional[ReasoningConfidence] = None

    # ── Arbitrary extras ──────────────────────────────────────────────────────
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Ensure chain has the correct execution_id
        if not self.chain.execution_id:
            self.chain = ReasoningChain(execution_id=self.execution_id)

    # ── Convenience helpers ───────────────────────────────────────────────────

    def all_collected_source_types(self) -> set[str]:
        """Return the set of evidence source types present in validated evidence."""
        return {ev.source_type for ev in self.validated_evidence}

    def source_ids(self) -> list[str]:
        """Return the flat list of all validated evidence source_ids."""
        return [ev.source_id for ev in self.validated_evidence]
