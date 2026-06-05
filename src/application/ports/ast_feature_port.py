"""Abstract port for AST feature extraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractedFeature:
    """A single feature extracted from the AST."""

    feature_type: str  # "call", "import", "decorator", "comparison", "string", "subscript"
    symbol: str  # e.g. "bcrypt.checkpw"
    line_number: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ASTFeatures:
    """Collection of features extracted from a specific AST block."""

    calls: list[ExtractedFeature] = field(default_factory=list)
    imports: list[ExtractedFeature] = field(default_factory=list)
    decorators: list[ExtractedFeature] = field(default_factory=list)
    comparisons: list[ExtractedFeature] = field(default_factory=list)
    strings: list[ExtractedFeature] = field(default_factory=list)
    subscripts: list[ExtractedFeature] = field(default_factory=list)
    data_flows: list[dict[str, Any]] = field(default_factory=list)


class IASTFeatureExtractor(ABC):
    """Abstract port for extracting AST features from code entities."""

    @abstractmethod
    def extract_features(
        self, tree: Any, source_code: str, start_line: int, end_line: int
    ) -> ASTFeatures:
        """
        Extract features from the AST within the specified line range.

        Args:
            tree: The tree-sitter AST.
            source_code: The raw file source code.
            start_line: The starting line (1-indexed, inclusive) of the code block.
            end_line: The ending line (1-indexed, inclusive) of the code block.

        Returns:
            An ASTFeatures collection containing all matched features.
        """
        pass
