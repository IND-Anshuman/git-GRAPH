from enum import Enum, auto

class AnalysisStatus(Enum):
    """Status of repository analysis."""
    PENDING = auto()
    CLONING = auto()
    SCANNING = auto()
    PARSING = auto()
    EXTRACTING = auto()
    COMPLETED = auto()
    FAILED = auto()
