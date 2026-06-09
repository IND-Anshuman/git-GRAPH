"""Repository interfaces for querying and registering metadata types, definitions, and embedding configurations."""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.meta_ontology import MetaType, MetaDefinition, EmbeddingModel, EmbeddingVersion


class IMetaTypeRepository(ABC):
    """Abstract interface for storing and retrieving MetaType dynamic definitions."""

    @abstractmethod
    def save(self, meta_type: MetaType) -> None:
        """Saves or updates a MetaType entry."""
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[MetaType]:
        """Retrieves a MetaType by its unique text key (e.g. 'Agent')."""
        pass

    @abstractmethod
    def list_all(self) -> List[MetaType]:
        """Lists all registered MetaTypes in the system."""
        pass

    @abstractmethod
    def list_by_category(self, category: str) -> List[MetaType]:
        """Lists registered MetaTypes filtered by category."""
        pass


class IMetaDefinitionRepository(ABC):
    """Abstract interface for storing and retrieving versioned MetaDefinitions."""

    @abstractmethod
    def save(self, meta_definition: MetaDefinition) -> None:
        """Saves a MetaDefinition revision."""
        pass

    @abstractmethod
    def get_by_version(self, type_id: str, major: int, minor: int, patch: int) -> Optional[MetaDefinition]:
        """Retrieves a MetaDefinition revision for a given type ID and version."""
        pass

    @abstractmethod
    def get_latest_definition(self, type_id: str) -> Optional[MetaDefinition]:
        """Retrieves the latest registered MetaDefinition revision for a type ID."""
        pass


class IEmbeddingModelRepository(ABC):
    """Abstract interface for querying and registering embedding models."""

    @abstractmethod
    def save(self, model: EmbeddingModel) -> None:
        """Saves or updates an EmbeddingModel entry."""
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[EmbeddingModel]:
        """Retrieves an EmbeddingModel entry by its ID."""
        pass

    @abstractmethod
    def get_active_model(self) -> Optional[EmbeddingModel]:
        """Retrieves the active embedding model selected in the registry."""
        pass


class IEmbeddingVersionRepository(ABC):
    """Abstract interface for querying and registering embedding versions."""

    @abstractmethod
    def save(self, version: EmbeddingVersion) -> None:
        """Saves an EmbeddingVersion configuration."""
        pass

    @abstractmethod
    def get_by_version(self, model_id: str, version_string: str) -> Optional[EmbeddingVersion]:
        """Retrieves an EmbeddingVersion by model ID and version string."""
        pass
