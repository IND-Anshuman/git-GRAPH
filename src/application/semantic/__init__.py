"""Phase 4.75 Bounded Context: Semantic Expansion."""

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
from src.application.semantic.embedding.embedding_registry import EmbeddingRegistry
from src.application.semantic.calibration.calibration_engine import ConfidenceCalibrationEngine
from src.application.semantic.schema.schema_registry import SchemaRegistry
from src.application.semantic.governance.governance_manager import GovernanceManager
from src.application.semantic.discovery.entity_discovery_engine import EntityDiscoveryEngine

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
    "EmbeddingRegistry",
    "ConfidenceCalibrationEngine",
    "SchemaRegistry",
    "GovernanceManager",
    "EntityDiscoveryEngine",
]
