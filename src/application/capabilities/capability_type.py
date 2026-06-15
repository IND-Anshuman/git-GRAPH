"""Classification enum for Capability domains."""

from enum import Enum

class CapabilityType(str, Enum):
    """Enumeration representing different domains of system capabilities."""
    BUSINESS = "BUSINESS"
    TECHNICAL = "TECHNICAL"
    PLATFORM = "PLATFORM"
    AI = "AI"
    SECURITY = "SECURITY"
    OPERATIONAL = "OPERATIONAL"
