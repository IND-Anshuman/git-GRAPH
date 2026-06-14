"""Repository Semantic Resolution Bounded Context."""

from .global_semantic_graph import GlobalSemanticGraph, CanonicalSymbol
from .symbol_resolution_engine import SymbolResolutionEngine
from .alias_propagation_engine import AliasPropagationEngine
from .cross_file_call_resolver import CrossFileCallResolver
from .external_dependency_resolver import ExternalDependencyResolver

__all__ = [
    "GlobalSemanticGraph",
    "CanonicalSymbol",
    "SymbolResolutionEngine",
    "AliasPropagationEngine",
    "CrossFileCallResolver",
    "ExternalDependencyResolver",
]
