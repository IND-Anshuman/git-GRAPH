from enum import Enum, auto

class RelationshipType(Enum):
    """Type of relationship between code entities."""
    CALLS = auto()
    IMPORTS = auto()
    DEPENDS_ON = auto()
    BELONGS_TO = auto()
    EXTENDS = auto()
    IMPLEMENTS = auto()
    READS = auto()
    WRITES = auto()
    USES = auto()
    TESTS = auto()
    DECORATES = auto()
