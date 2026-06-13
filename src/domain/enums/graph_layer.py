from enum import Enum, auto

class GraphLayer(Enum):
    """Logical layer of the knowledge graph."""
    STRUCTURAL = auto()
    SEMANTIC = auto()
    BEHAVIOR = auto()
    CONCEPT = auto()
    CAPABILITY = auto()
    REASONING = auto()
