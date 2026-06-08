"""Generics and type signature normalizer."""

import re
from typing import List, Tuple


class GenericNormalizer:
    """Utility to normalize generic declarations and interface prefixes."""

    @staticmethod
    def strip_generic_wrappers(type_sig: str) -> Tuple[str, List[str]]:
        """
        Strips outer generic/interface wrapper from type signature.
        
        Examples:
            "IRepository<User>" -> ("Repository", ["User"])
            "Repository<User>" -> ("Repository", ["User"])
            "IUserService" -> ("UserService", [])
        """
        if not type_sig:
            return "", []

        stripped = type_sig.strip()

        # Match generic structure: Name<Args> or Name[Args]
        match = re.match(r"^I?([A-Za-z0-9_]+)[<\[](.+)[>\]]$", stripped)
        if match:
            base_name = match.group(1)
            args_str = match.group(2)
            args = [a.strip() for a in args_str.split(",")]
            return base_name, args

        # Strip 'I' interface prefix if it is followed by an uppercase letter
        if stripped.startswith("I") and len(stripped) > 1 and stripped[1].isupper():
            return stripped[1:], []

        return stripped, []
