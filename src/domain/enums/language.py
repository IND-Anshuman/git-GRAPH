from enum import Enum, auto

class SupportedLanguage(Enum):
    """Programming language of a source file."""
    PYTHON = auto()
    JAVASCRIPT = auto()
    TYPESCRIPT = auto()
    GO = auto()
    JAVA = auto()
    CSHARP = auto()
    RUST = auto()
    KOTLIN = auto()
    SWIFT = auto()
    PHP = auto()
    SCALA = auto()
    RUBY = auto()
    ELIXIR = auto()
    HTML = auto()
    CSS = auto()
    UNKNOWN = auto()
