from enum import Enum, auto

class SupportedLanguage(Enum):
    """Programming language of a source file."""
    PYTHON = auto()
    JAVASCRIPT = auto()
    TYPESCRIPT = auto()
    GO = auto()
    JAVA = auto()
    UNKNOWN = auto()
