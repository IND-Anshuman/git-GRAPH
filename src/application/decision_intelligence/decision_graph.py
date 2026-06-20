from typing import List, Dict, Any
from .decision import Decision

class DecisionGraph:
    def __init__(self, decisions: List[Decision], dependencies: List[Any]):
        self.decisions = decisions
        self.dependencies = dependencies
        
    def to_networkx(self):
        pass
        
    def get_roots(self) -> List[Decision]:
        return []
