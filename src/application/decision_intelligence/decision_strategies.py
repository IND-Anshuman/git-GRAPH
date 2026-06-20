from typing import Dict, Any, List

class DecisionDiscoveryStrategy:
    def execute(self, context: Any) -> Dict[str, Any]:
        return {"decisions": []}

class IntentDetectionStrategy:
    def execute(self, context: Any) -> Dict[str, Any]:
        return {"intents": []}
