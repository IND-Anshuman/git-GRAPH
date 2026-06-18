"""
Phase 7A — ReasoningChain

Encapsulates a step-by-step trace of the reasoning pipeline so that:
  * Engineers can debug exactly which inferences were made.
  * UI explanation generators can walk steps to produce narratives.
  * Governance audits can validate that each conclusion logically follows
    from its predecessors.

Each :class:`ReasoningStep` records one atomic inference or data-fetch
within the pipeline.  The :class:`ReasoningChain` preserves the ordered
sequence of all steps for a reasoning run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ReasoningStep:
    """One atomic step in the reasoning pipeline.

    Attributes:
        step_index:   Zero-based position in the pipeline.
        step_type:    Category of step (``"evidence_collection"``,
                      ``"evidence_expansion"``, ``"validation"``,
                      ``"hypothesis_generation"``, ``"hypothesis_scoring"``,
                      ``"conclusion"``).
        description:  Human-readable description of what this step did.
        inputs:       IDs or descriptors of the inputs consumed.
        outputs:      IDs or descriptors of the outputs produced.
        executed_at:  UTC timestamp when the step was executed.
        duration_ms:  Wall-clock duration in milliseconds (optional).
        metadata:     Arbitrary extra debug data.
    """

    step_index: int
    step_type: str
    description: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    executed_at: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_index": self.step_index,
            "step_type": self.step_type,
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "executed_at": self.executed_at.isoformat(),
            "duration_ms": self.duration_ms,
        }


@dataclass
class ReasoningChain:
    """Ordered sequence of all reasoning steps for one execution run.

    Attributes:
        execution_id: Links back to the parent :class:`ReasoningResult`.
        steps:        Ordered list of :class:`ReasoningStep` instances.
    """

    execution_id: str
    steps: list[ReasoningStep] = field(default_factory=list)

    # ── Mutation helpers ──────────────────────────────────────────────────────

    def add_step(
        self,
        step_type: str,
        description: str,
        inputs: list[str] | None = None,
        outputs: list[str] | None = None,
        duration_ms: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ReasoningStep:
        """Append a new step and return it."""
        step = ReasoningStep(
            step_index=len(self.steps),
            step_type=step_type,
            description=description,
            inputs=inputs or [],
            outputs=outputs or [],
            duration_ms=duration_ms,
            metadata=metadata or {},
        )
        self.steps.append(step)
        return step

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "total_steps": len(self.steps),
            "steps": [s.to_dict() for s in self.steps],
        }
