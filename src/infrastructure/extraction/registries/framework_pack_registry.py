import yaml
from pathlib import Path
from typing import Dict, List, Any

class FrameworkPackRegistry:
    def __init__(self, data_dir: Path | None = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent.parent.parent.parent / "data" / "framework_packs"
        else:
            self.data_dir = data_dir
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get_pack(self, name: str) -> Dict[str, Any]:
        if name in self._cache:
            return self._cache[name]
        
        pack_path = self.data_dir / f"{name}.yaml"
        if not pack_path.exists():
            return {"entities": {}, "decorators": {}, "relationships": {}}
        
        with open(pack_path, "r", encoding="utf-8") as f:
            pack_data = yaml.safe_load(f) or {}

        resolved = {"entities": {}, "decorators": {}, "relationships": {}}
        
        # Resolve inherits
        inherits = pack_data.get("inherits", [])
        for parent in inherits:
            parent_resolved = self.get_pack(parent)
            # Deep merge
            for key in ["entities", "decorators", "relationships"]:
                resolved[key].update(parent_resolved.get(key, {}))
        
        # Merge self
        for key in ["entities", "decorators", "relationships"]:
            resolved[key].update(pack_data.get(key, {}))
            
        self._cache[name] = resolved
        return resolved
