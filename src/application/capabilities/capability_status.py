"""Lifecycle status enum for capabilities."""

from enum import Enum

class CapabilityStatus(str, Enum):
    """States of a capability across its lifecycle."""
    CANDIDATE = "CANDIDATE"
    DISCOVERED = "DISCOVERED"
    VERIFIED = "VERIFIED"
    DEPRECATED = "DEPRECATED"
