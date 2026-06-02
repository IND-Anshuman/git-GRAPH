from enum import Enum

class MutationType(str, Enum):
    """Types of mutation that can occur on graph entities and relationships."""
    CREATED = "CREATED"
    MODIFIED = "MODIFIED"
    RENAMED = "RENAMED"
    MOVED = "MOVED"
    DELETED = "DELETED"
