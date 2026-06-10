import yaml
from pathlib import Path
from typing import Dict, List, Any

class CapabilityRegistry:
    def __init__(self, file_path: Path | None = None):
        if file_path is None:
            self.file_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "capability_registry.yaml"
        else:
            self.file_path = file_path
        self._capabilities: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        if not self.file_path.exists():
            return
        with open(self.file_path, "r", encoding="utf-8") as f:
            self._capabilities = yaml.safe_load(f) or {}

    def get_capabilities(self) -> Dict[str, Dict[str, Any]]:
        return self._capabilities
