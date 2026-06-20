from typing import List, Dict, Any
from .intent import Intent

class IntentGraph:
    def __init__(self, intents: List[Intent], relationships: List[Any]):
        self.intents = intents
        self.relationships = relationships
