"""Value object representing a multi-dimensional fingerprint for a logic version."""

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class LogicFingerprint:
    """
    Immutable fingerprint capturing the structural, dependency, and behavioral
    characteristics of a detected logic implementation.

    All three component hashes are combined into a single composite SHA-256
    digest that uniquely identifies an exact implementation.
    """

    structure_hash: str
    """SHA-256 of the canonical AST structure of the implementation."""

    dependency_hash: str
    """SHA-256 of the external calls and import symbols used."""

    behavioral_hash: str
    """SHA-256 of derived behavioral feature indicators."""

    composite: str
    """SHA-256 of (structure_hash + dependency_hash + behavioral_hash)."""

    @classmethod
    def compute(
        cls,
        structure_hash: str,
        dependency_hash: str,
        behavioral_hash: str,
    ) -> "LogicFingerprint":
        """
        Construct a LogicFingerprint by computing the composite hash from its three components.

        Args:
            structure_hash: Pre-computed canonical AST structure hash.
            dependency_hash: Pre-computed external call/import hash.
            behavioral_hash: Pre-computed behavioral feature indicators hash.

        Returns:
            A new immutable LogicFingerprint instance.
        """
        raw = structure_hash + dependency_hash + behavioral_hash
        composite = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return cls(
            structure_hash=structure_hash,
            dependency_hash=dependency_hash,
            behavioral_hash=behavioral_hash,
            composite=composite,
        )

    @property
    def value(self) -> str:
        """Return the composite hash (alias for backward compatibility)."""
        return self.composite

    def __eq__(self, other: object) -> bool:
        """Equality is determined solely by the composite hash."""
        if not isinstance(other, LogicFingerprint):
            return NotImplemented
        return self.composite == other.composite

    def __hash__(self) -> int:
        return hash(self.composite)
