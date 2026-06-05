"""Engine for computing semantic and structural similarity between logic implementations."""

from src.domain.entities.logic_version import LogicVersion
from src.domain.value_objects.logic_fingerprint import LogicFingerprint


class LogicSimilarityEngine:
    """Computes similarity scores between logic implementations using their fingerprints."""

    def compute_similarity(
        self, fingerprint_a: LogicFingerprint, fingerprint_b: LogicFingerprint
    ) -> float:
        """
        Compute a similarity score in [0.0, 1.0] between two LogicFingerprints.

        The score is a weighted average of equality across the three component hashes:
            Structure   → 0.40
            Dependency  → 0.35
            Behavioral  → 0.25
        """
        # Cryptographic hashes are compared strictly for equality
        struct_sim = (
            1.0 if fingerprint_a.structure_hash == fingerprint_b.structure_hash else 0.0
        )
        dep_sim = (
            1.0 if fingerprint_a.dependency_hash == fingerprint_b.dependency_hash else 0.0
        )
        beh_sim = (
            1.0 if fingerprint_a.behavioral_hash == fingerprint_b.behavioral_hash else 0.0
        )

        return 0.40 * struct_sim + 0.35 * dep_sim + 0.25 * beh_sim

    def compute_version_similarity(
        self, version_a: LogicVersion, version_b: LogicVersion
    ) -> float:
        """Compute the similarity score between two LogicVersions."""
        return self.compute_similarity(version_a.fingerprint, version_b.fingerprint)
