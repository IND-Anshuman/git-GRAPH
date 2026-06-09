"""Value object representing a composite behaviour fingerprint of a code snippet or method."""

import re
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(frozen=True)
class CompositeBehaviorFingerprint:
    """Contains multi-dimensional fingerprints representing execution patterns."""

    ast_shape: str = ""
    call_signature: str = ""
    import_signature: str = ""
    data_flow_signature: str = ""
    semantic_tokens: str = ""
    framework_context: str = ""

    def calculate_similarity(self, other: "CompositeBehaviorFingerprint") -> float:
        """Computes the weighted composite similarity between two fingerprints.

        Formula:
        Similarity = 0.25*AST + 0.25*Calls + 0.15*Imports + 0.20*DataFlow + 0.15*Tokens
        """
        ast_sim = self._jaccard_similarity(self.ast_shape, other.ast_shape)
        calls_sim = self._jaccard_similarity(self.call_signature, other.call_signature)
        imports_sim = self._jaccard_similarity(self.import_signature, other.import_signature)
        df_sim = self._jaccard_similarity(self.data_flow_signature, other.data_flow_signature)
        tokens_sim = self._jaccard_similarity(self.semantic_tokens, other.semantic_tokens)

        return (
            0.25 * ast_sim
            + 0.25 * calls_sim
            + 0.15 * imports_sim
            + 0.20 * df_sim
            + 0.15 * tokens_sim
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes this value object to a dictionary."""
        return {
            "ast_shape": self.ast_shape,
            "call_signature": self.call_signature,
            "import_signature": self.import_signature,
            "data_flow_signature": self.data_flow_signature,
            "semantic_tokens": self.semantic_tokens,
            "framework_context": self.framework_context,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CompositeBehaviorFingerprint":
        """Deserializes a dictionary to a CompositeBehaviorFingerprint."""
        if not d:
            return cls()
        return cls(
            ast_shape=d.get("ast_shape", ""),
            call_signature=d.get("call_signature", ""),
            import_signature=d.get("import_signature", ""),
            data_flow_signature=d.get("data_flow_signature", ""),
            semantic_tokens=d.get("semantic_tokens", ""),
            framework_context=d.get("framework_context", ""),
        )

    @staticmethod
    def _jaccard_similarity(s1: str, s2: str) -> float:
        """Helper to calculate Jaccard similarity between tokenized strings."""
        if not s1 or not s2:
            return 1.0 if s1 == s2 else 0.0

        # Tokenize by commas or spaces
        tokens1 = set(t for t in re.split(r"[,\s]+", s1) if t)
        tokens2 = set(t for t in re.split(r"[,\s]+", s2) if t)

        if not tokens1 or not tokens2:
            return 1.0 if tokens1 == tokens2 else 0.0

        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        return intersection / union
