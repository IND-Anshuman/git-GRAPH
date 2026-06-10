import yaml
from pathlib import Path
from typing import Dict, List

class SemanticHintRegistry:
    def __init__(self, file_path: Path | None = None):
        if file_path is None:
            self.file_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "semantic_hint_registry.yaml"
        else:
            self.file_path = file_path
        self._hints: Dict[str, List[str]] = {}
        self._load()

    def _load(self):
        if not self.file_path.exists():
            return
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        for category, config in data.items():
            tokens = config.get("tokens", [])
            self._hints[category] = tokens

    def get_hints_for_token(self, token: str) -> List[str]:
        matches = []
        token_lower = token.lower()
        for category, tokens in self._hints.items():
            for t in tokens:
                if t in token_lower:
                    matches.append(category)
                    break
        return matches
