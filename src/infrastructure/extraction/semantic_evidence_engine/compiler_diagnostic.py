from dataclasses import dataclass

@dataclass(frozen=True)
class CompilerDiagnostic:
    severity: str  # ERROR, WARNING, INFO
    category: str  # PARSING, SYMBOL_RESOLUTION, FRAMEWORK, FLOW, DATAFLOW, AI, FRONTEND
    code: str      # UNKNOWN_DECORATOR, UNKNOWN_IMPORT, etc.
    message: str
    evidence: list[str]
