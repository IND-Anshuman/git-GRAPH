"""Phase 4.5 Bounded Context: Semantic Expansion."""

from src.application.semantic.type_resolution.type_resolution_engine import TypeResolutionEngine
from src.application.semantic.type_resolution.generic_normalizer import GenericNormalizer
from src.application.semantic.normalization.semantic_normalizer import SemanticNormalizer
from src.application.semantic.normalization.normalization_rules import NormalizationRules
from src.application.semantic.frameworks.framework_registry import FrameworkRegistry
from src.application.semantic.frameworks.framework_version import FrameworkVersion
from src.application.semantic.behavior_registry.canonical_registry import (
    CanonicalRegistry,
    BehaviorFamily,
    BehaviorMappingRule,
    CanonicalBehaviorDefinition,
)
from src.application.semantic.behavior_registry.ontology_mapper import OntologyMapper

__all__ = [
    "TypeResolutionEngine",
    "GenericNormalizer",
    "SemanticNormalizer",
    "NormalizationRules",
    "FrameworkRegistry",
    "FrameworkVersion",
    "CanonicalRegistry",
    "BehaviorFamily",
    "BehaviorMappingRule",
    "CanonicalBehaviorDefinition",
    "OntologyMapper",
]
