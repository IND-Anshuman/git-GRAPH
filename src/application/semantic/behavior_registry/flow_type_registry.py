"""Registry for canonical flow types including default and dynamically added categories."""

from typing import List, Set


class FlowTypeRegistry:
    """In-memory registry for flow types dynamically discovered or predefined in the system."""

    def __init__(self) -> None:
        self._flow_types: Set[str] = set()
        self._load_defaults()

    def _load_defaults(self) -> None:
        defaults = [
            "Execution Flow",
            "Messaging Flow",
            "AI Flow",
            "Frontend Flow",
            "Workflow Flow",
            "Data Pipeline Flow",
            "Feature Flag Flow",
            "Observability Flow",
            "ETL Flow",
        ]
        for dt in defaults:
            self.register_flow_type(dt)

    def register_flow_type(self, flow_type: str) -> None:
        """Registers a new flow type key in the system."""
        if flow_type:
            # Canonicalize representation (e.g. "AI Flow" or "AI_FLOW")
            self._flow_types.add(flow_type.strip())

    def list_flow_types(self) -> List[str]:
        """Lists all registered flow types."""
        return sorted(list(self._flow_types))

    def is_supported(self, flow_type: str) -> bool:
        """Checks if a given flow type string is registered."""
        if not flow_type:
            return False
        cleaned = flow_type.strip()
        # Direct check or case-insensitive check
        if cleaned in self._flow_types:
            return True
        for t in self._flow_types:
            if t.lower() == cleaned.lower() or t.replace(" ", "_").lower() == cleaned.lower():
                return True
        return False
