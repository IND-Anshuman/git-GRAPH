"""Type resolution engine for binding interfaces, traits, and generics."""

from typing import Any, Dict, List
from src.application.semantic.type_resolution.generic_normalizer import GenericNormalizer


class TypeResolutionEngine:
    """Resolves namespaces, imports, and generic type parameters statically."""

    def resolve_type(self, type_string: str) -> Dict[str, Any]:
        """
        Resolves type string into normalized base name and generic arguments.
        
        Args:
            type_string: Raw type string from AST parse.
            
        Returns:
            Dict containing resolved metadata.
        """
        base_name, generic_args = GenericNormalizer.strip_generic_wrappers(type_string)
        return {
            "original": type_string,
            "normalized_base": base_name,
            "generic_args": generic_args,
            "is_generic": len(generic_args) > 0,
        }

    def bind_interface_methods(self, class_name: str, interfaces: List[str], methods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Binds interface generics to concrete method parameters.
        
        Args:
            class_name: Target implementing class.
            interfaces: Base interfaces list.
            methods: Extracted method structures.
            
        Returns:
            List of methods with resolved type descriptors.
        """
        bound_methods = []
        for method in methods:
            m_copy = method.copy()
            if m_copy.get("return_type"):
                m_copy["resolved_return_type"] = self.resolve_type(m_copy["return_type"])
            else:
                m_copy["resolved_return_type"] = {"normalized_base": "void", "generic_args": [], "is_generic": False}
            bound_methods.append(m_copy)
        return bound_methods
