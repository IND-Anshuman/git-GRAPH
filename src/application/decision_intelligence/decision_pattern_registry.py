import yaml
import os
from typing import Dict, Any, List

class DecisionPatternRegistry:
    def __init__(self, registry_dir: str):
        self.registry_dir = registry_dir
        self.patterns: Dict[str, Any] = {}
        self._load_patterns()
        
    def _load_patterns(self):
        if not os.path.exists(self.registry_dir):
            return
            
        for file in os.listdir(self.registry_dir):
            if file.endswith(('.yml', '.yaml')):
                path = os.path.join(self.registry_dir, file)
                with open(path, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and 'patterns' in data:
                        for pattern in data['patterns']:
                            self.patterns[pattern['id']] = pattern
                            
    def get_pattern(self, pattern_id: str) -> Any:
        return self.patterns.get(pattern_id)
        
    def match_patterns(self, text: str) -> List[Any]:
        matches = []
        text_lower = text.lower()
        for pattern in self.patterns.values():
            keywords = pattern.get('keywords', [])
            if any(k.lower() in text_lower for k in keywords):
                matches.append(pattern)
        return matches
