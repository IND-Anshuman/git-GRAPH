from dataclasses import dataclass
import hashlib

@dataclass(frozen=True)
class StructuralFingerprint:
    """A fingerprint representing the structural hash of a code entity."""
    value: str

    @staticmethod
    def compute(source_text: str) -> "StructuralFingerprint":
        """Compute a structural fingerprint from source text using SHA-256."""
        hash_val = hashlib.sha256(source_text.encode('utf-8')).hexdigest()
        return StructuralFingerprint(value=hash_val)
