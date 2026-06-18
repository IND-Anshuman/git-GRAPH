"""
Phase 7A — ReasoningLimitation

Explicitly documents gaps, missing data, or incomplete coverage in a
reasoning result.  Every :class:`~reasoning_result.ReasoningResult` MUST
carry a (possibly empty) list of limitations.

Without limitations, consumers of the reasoning API would over-trust outputs
and make incorrect decisions.  Explicit limitations enable:

  * **Transparency**  — the user sees exactly what data is missing.
  * **Trust calibration** — downstream systems can discount the result
    proportionally.
  * **Governance**   — audit trails show known gaps at the time of the query.
  * **Actionability** — engineers know which data to collect to improve results.

Example limitations
-------------------
  * "Cross-repository dependencies unavailable — blast radius may be incomplete."
  * "Ownership data incomplete — no CODEOWNERS file found."
  * "Historical timeline missing before commit abc1234."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ReasoningLimitation:
    """Documents a specific gap or missing data in a reasoning result.

    Attributes:
        reason:        Short, descriptive explanation of *why* this limitation
                       exists (e.g. "Cross-repository dependencies unavailable").
        affected_area: The part of the reasoning that is incomplete
                       (e.g. "blast_radius", "ownership", "timeline").
        impact:        How this limitation affects the result's reliability
                       (e.g. "Blast radius may under-count impacted services").
    """

    reason: str
    affected_area: str
    impact: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "reason": self.reason,
            "affected_area": self.affected_area,
            "impact": self.impact,
        }

    def __str__(self) -> str:
        return f"[{self.affected_area}] {self.reason} → {self.impact}"
