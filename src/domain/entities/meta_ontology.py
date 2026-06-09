"""Domain entities representing Meta-Ontology, schema schemas, and embedding registry configurations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class MetaType:
    """Represents a dynamically discovered semantic entity or relationship type identifier."""

    id: str  # E.g. "Agent", "Saga", "Component"
    name: str
    category: str  # STRUCTURAL, BEHAVIORAL, CONCEPTUAL, INTERACTION_FLOW
    status: str = "EXPERIMENTAL"  # EXPERIMENTAL, CANDIDATE, ACTIVE, DEPRECATED
    created_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> None:
        if not self.id:
            raise ValueError("MetaType id cannot be empty.")
        if not self.name:
            raise ValueError("MetaType name cannot be empty.")
        if self.category not in {"STRUCTURAL", "BEHAVIORAL", "CONCEPTUAL", "INTERACTION_FLOW"}:
            raise ValueError(f"Invalid category: {self.category}")
        if self.status not in {"EXPERIMENTAL", "CANDIDATE", "ACTIVE", "DEPRECATED"}:
            raise ValueError(f"Invalid status: {self.status}")


@dataclass
class MetaDefinition:
    """Represents a versioned schema structure configuration for a dynamically registered MetaType."""

    id: uuid.UUID
    type_id: str
    major_version: int
    minor_version: int
    patch_version: int
    schema_definition: Dict[str, Any]  # JSON Schema validating instances
    semantic_signature: Dict[str, Any]  # Key attributes matching discovery patterns
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def version_string(self) -> str:
        return f"{self.major_version}.{self.minor_version}.{self.patch_version}"

    def validate(self) -> None:
        if not self.type_id:
            raise ValueError("MetaDefinition type_id cannot be empty.")
        if self.major_version < 0 or self.minor_version < 0 or self.patch_version < 0:
            raise ValueError("Version fields must be non-negative integers.")
        if not isinstance(self.schema_definition, dict):
            raise ValueError("schema_definition must be a dictionary.")


@dataclass
class EmbeddingModel:
    """Represents a vector model configuration registered in the EmbeddingRegistry."""

    id: str  # E.g. "text-embedding-3-small"
    model_name: str
    provider: str  # local, openai, huggingface
    dimensions: int
    distance_metric: str  # cosine, l2, ip
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> None:
        if not self.id:
            raise ValueError("EmbeddingModel id cannot be empty.")
        if self.dimensions <= 0:
            raise ValueError("Dimensions must be a positive integer.")
        if self.distance_metric not in {"cosine", "l2", "ip"}:
            raise ValueError(f"Invalid distance_metric: {self.distance_metric}")


@dataclass
class EmbeddingVersion:
    """Represents a specific registered structural configuration of an EmbeddingModel."""

    id: uuid.UUID
    model_id: str
    version_string: str  # SemVer e.g. "1.0.0"
    configuration: Dict[str, Any]  # hyperparams like pooling, prefix prompts
    registered_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> None:
        if not self.model_id:
            raise ValueError("EmbeddingVersion model_id cannot be empty.")
        if not self.version_string:
            raise ValueError("EmbeddingVersion version_string cannot be empty.")


@dataclass
class SemanticEvidence:
    """Represents raw code audit tokens supporting a discovery classification."""

    matched_imports: List[str] = field(default_factory=list)
    matched_calls: List[str] = field(default_factory=list)
    matched_heuristics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticConfidence:
    """Calibration details representing subsystem scoring certainty."""

    overall_score: float
    bayesian_prior: float = 0.5
    evidence_density: float = 0.0
    structural_density: float = 0.0
