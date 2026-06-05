"""Registry for loading, indexing, and serving behavioral patterns."""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Set
import yaml

from src.domain.entities.behavior_pattern import BehaviorPattern
from src.domain.exceptions import OntologyLoadException  # Reuse load exception for patterns


class PatternRegistry:
    """Registry that holds loaded BehaviorPatterns and indexes them by lookup keys."""

    def __init__(self) -> None:
        self._patterns_by_id: Dict[str, BehaviorPattern] = {}
        self._patterns_by_key: Dict[str, List[BehaviorPattern]] = {}

    def load_from_directory(self, directory_path: str) -> List[BehaviorPattern]:
        """
        Load pattern definitions from YAML files in the given directory.

        Args:
            directory_path: Absolute path to the patterns directory.

        Returns:
            A list of all loaded BehaviorPattern entities.
        """
        if not os.path.isdir(directory_path):
            raise OntologyLoadException(
                f"Patterns directory does not exist: {directory_path}"
            )

        loaded_patterns = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                filepath = os.path.join(directory_path, filename)
                loaded_patterns.extend(self._load_from_file(filepath))

        return loaded_patterns

    def register_patterns(self, patterns: List[BehaviorPattern]) -> None:
        """Register patterns in the registry and update indexes."""
        for pattern in patterns:
            self._patterns_by_id[pattern.pattern_id] = pattern

            # Index by keys
            for key in pattern.index_keys:
                if key not in self._patterns_by_key:
                    self._patterns_by_key[key] = []
                # Avoid duplicates
                if (
                    pattern
                    not in self._patterns_by_key[key]
                ):
                    self._patterns_by_key[key].append(pattern)

    def get_by_pattern_id(self, pattern_id: str) -> BehaviorPattern | None:
        """Retrieve a pattern by its ID."""
        return self._patterns_by_id.get(pattern_id)

    def get_all_patterns(self) -> List[BehaviorPattern]:
        """Retrieve all registered patterns."""
        return list(self._patterns_by_id.values())

    def get_candidate_patterns(self, index_keys: List[str]) -> List[BehaviorPattern]:
        """
        Find candidate patterns that match any of the provided index keys.

        Args:
            index_keys: List of lookup keys (e.g. ['call:bcrypt.checkpw', 'import:bcrypt']).

        Returns:
            A list of unique candidate BehaviorPattern entities.
        """
        candidates: Dict[str, BehaviorPattern] = {}
        for key in index_keys:
            if key in self._patterns_by_key:
                for pattern in self._patterns_by_key[key]:
                    candidates[pattern.pattern_id] = pattern
        return list(candidates.values())

    def clear(self) -> None:
        """Clear all registered patterns and indexes."""
        self._patterns_by_id.clear()
        self._patterns_by_key.clear()

    def _load_from_file(self, file_path: str) -> List[BehaviorPattern]:
        """Load and parse patterns from a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise OntologyLoadException(
                f"Failed to read/parse pattern YAML in {file_path}: {e}"
            ) from e

        if not data:
            return []

        schema_version = data.get("schema_version", "1.0")
        raw_patterns = data.get("patterns", [])
        if not isinstance(raw_patterns, list):
            raise OntologyLoadException(
                f"'patterns' must be a list in file: {file_path}"
            )

        patterns = []
        for raw in raw_patterns:
            pattern_id = raw.get("pattern_id")
            name = raw.get("name")
            ontology_node_id = raw.get("ontology_node_id")
            base_confidence = raw.get("base_confidence", 1.0)
            pattern_version = raw.get("pattern_version", "1.0.0")
            rules = raw.get("rules", {})
            index_keys = raw.get("index_keys", [])

            if not pattern_id:
                raise OntologyLoadException(
                    f"Pattern missing 'pattern_id' in: {file_path}"
                )
            if not name:
                raise OntologyLoadException(
                    f"Pattern {pattern_id} missing 'name' in: {file_path}"
                )
            if not ontology_node_id:
                raise OntologyLoadException(
                    f"Pattern {pattern_id} missing 'ontology_node_id' in: {file_path}"
                )

            # Generate a stable UUID for the pattern
            # Using UUID5 based on the pattern_id for determinism
            namespace = uuid.UUID("d34e5678-a89c-4828-9717-d1a1b15c9ff8")
            pat_uuid = uuid.uuid5(namespace, pattern_id)

            pattern = BehaviorPattern(
                id=pat_uuid,
                pattern_id=pattern_id,
                name=name,
                ontology_node_id=ontology_node_id,
                base_confidence=float(base_confidence),
                pattern_version=pattern_version,
                schema_version=schema_version,
                rules=rules,
                index_keys=index_keys,
                is_active=True,
                loaded_at=datetime.utcnow(),
            )
            patterns.append(pattern)

        return patterns
