"""Enum defining the types of evidence that support a logic detection result."""

from enum import Enum


class EvidenceType(str, Enum):
    """Classification of evidence that supports a behavior detection."""

    AST_CALL = "AST_CALL"
    """A function or method call matched a pattern rule."""

    AST_IMPORT = "AST_IMPORT"
    """An import statement matched a known symbol."""

    DATA_FLOW = "DATA_FLOW"
    """A parameter flows to a matched sink."""

    PATTERN_RULE = "PATTERN_RULE"
    """A composite pattern rule was fully satisfied."""

    DEPENDENCY = "DEPENDENCY"
    """A package-level dependency matched a known library."""

    STRUCTURAL = "STRUCTURAL"
    """The AST structure shape matched a known pattern."""
