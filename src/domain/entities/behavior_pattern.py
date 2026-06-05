"""Domain entity representing a loaded behavior pattern definition."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class BehaviorPattern:
    """
    A BehaviorPattern is the in-memory representation of a YAML-defined detection rule.

    Patterns are loaded at startup from the pattern catalog and used by the logic
    extraction engine to match implementations against named behavioral contracts.
    They are refreshed via delete_all + save_batch when the YAML catalog is reloaded.
    """

    id: uuid.UUID
    """Unique identifier for this loaded pattern record."""

    pattern_id: str
    """Stable, human-readable pattern identifier (e.g., 'auth_bcrypt_verification')."""

    name: str
    """Display name of the pattern (e.g., 'Bcrypt Password Verification')."""

    ontology_node_id: str
    """Dot-path reference into the ontology tree (e.g., 'security.authentication.hash_comparison')."""

    base_confidence: float
    """Default confidence weight assigned when this pattern fully matches."""

    pattern_version: str
    """Semantic version of the pattern definition (e.g., '1.0.0')."""

    schema_version: str
    """Version of the pattern YAML schema used (e.g., '1.0')."""

    rules: dict[str, Any] = field(default_factory=dict)
    """Serialized rule definitions from the YAML catalog (sub-rules, weights, etc.)."""

    index_keys: list[str] = field(default_factory=list)
    """Pre-computed lookup keys for fast index matching (e.g., ['call:bcrypt.checkpw', 'import:bcrypt'])."""

    is_active: bool = True
    """False if this pattern has been administratively disabled."""

    loaded_at: datetime = field(default_factory=datetime.utcnow)
    """UTC timestamp when this pattern was loaded into the database."""
