from typing import List, Dict, Any
from .decision import Decision
from .decision_impact import DecisionImpact

class DecisionImpactEngine:
    def calculate_impact(self, decision: Decision, architecture_graph: Any) -> DecisionImpact:
        return DecisionImpact(
            affected_capabilities=[],
            affected_architectures=[],
            affected_services=[],
            affected_dependencies=[],
            affected_ai_systems=[]
        )
