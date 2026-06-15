"""Domain model representing cryptographic capability fingerprints."""

from dataclasses import dataclass

@dataclass
class CapabilityFingerprint:
    """Hash signatures of capability sub-elements for similarity comparison and change detection."""
    capability_id: str
    concept_signature: str
    behavior_signature: str
    flow_signature: str
    relationship_signature: str
    architecture_signature: str
