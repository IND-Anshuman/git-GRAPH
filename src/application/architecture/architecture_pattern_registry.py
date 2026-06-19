"""Pattern registry for loading architecture signatures from YAML configuration."""

import os
import yaml
from typing import Dict, Any, List

class ArchitecturePatternRegistry:
    """
    Loads architecture signatures from YAML configurations, avoiding hardcoded patterns
    in Python. These signatures describe topology rules, required capabilities, and
    forbidden dependencies.
    """

    def __init__(self, patterns_dir: str) -> None:
        """Initialize the registry and load patterns from the given directory."""
        self.patterns_dir = patterns_dir
        self._patterns: Dict[str, Dict[str, Any]] = {}
        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load all YAML files from the patterns directory."""
        if not os.path.exists(self.patterns_dir):
            return

        for filename in os.listdir(self.patterns_dir):
            if filename.endswith((".yaml", ".yml")):
                filepath = os.path.join(self.patterns_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data and isinstance(data, dict):
                            for key, value in data.items():
                                self._patterns[key] = value
                except Exception as e:
                    # In a real app we'd log this, but we silently skip for now
                    pass

    def get_pattern(self, pattern_name: str) -> Dict[str, Any]:
        """Retrieve a specific pattern by name."""
        return self._patterns.get(pattern_name, {})

    def get_all_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve all loaded patterns."""
        return self._patterns
