"""LLM-ready summary generation for capabilities."""

from typing import Any

class CapabilitySummary:
    """Generates natural language capability summaries and details for future LLM reasoning consumption."""

    def generate_summary(self, capability: Any) -> str:
        """
        Synthesizes a descriptive text summary using concepts, coverage, and dependencies.
        """
        concepts_list = capability.concepts if capability.concepts else ["generic actions"]
        entities_count = len(capability.coverage.entities) if capability.coverage else 0
        apis_count = len(capability.coverage.apis) if capability.coverage else 0

        summary_text = (
            f"The {capability.name} capability provides system functionality "
            f"linked to {', '.join(concepts_list[:3])}. "
            f"It is implemented across {entities_count} code entities "
            f"and covers {apis_count} exposed APIs."
        )
        return summary_text
