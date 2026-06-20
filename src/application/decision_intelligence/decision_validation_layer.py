from typing import List
from .decision import Decision

class DecisionValidationLayer:
    def validate(self, decisions: List[Decision]) -> List[Decision]:
        valid_decisions = []
        for decision in decisions:
            # Must have confidence > threshold
            if decision.confidence.score > 0.3:
                # Must have at least some evidence
                if (decision.supporting_evidence.supporting_commits or 
                    decision.supporting_evidence.supporting_documents or
                    decision.supporting_evidence.supporting_repository_events or
                    decision.supporting_evidence.supporting_architecture_changes):
                    valid_decisions.append(decision)
                    
        return valid_decisions
