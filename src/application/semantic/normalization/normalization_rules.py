"""Custom normalization rules and formatting helpers."""

import re


class NormalizationRules:
    """Provides utility methods for syntax string normalization."""

    @staticmethod
    def normalize_method_name(name: str) -> str:
        """
        Converts camelCase, PascalCase, or snake_case to a unified snake_case format.
        
        Examples:
            "VerifyHashedPassword" -> "verify_hashed_password"
            "checkpw" -> "checkpw"
        """
        if not name:
            return ""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        return s2.lower().replace("__", "_")
