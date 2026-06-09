"""Embedding Registry service to manage embedding models, versions, and validation."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.entities.meta_ontology import EmbeddingModel, EmbeddingVersion


class EmbeddingRegistry:
    """Manages registration, activation, validation, and version tracking of embedding models."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    def register_model(
        self,
        model_id: str,
        model_name: str,
        provider: str,
        dimensions: int,
        distance_metric: str,
        is_active: bool = False,
    ) -> EmbeddingModel:
        """Registers a new embedding model in the registry."""
        model = EmbeddingModel(
            id=model_id,
            model_name=model_name,
            provider=provider,
            dimensions=dimensions,
            distance_metric=distance_metric,
            is_active=is_active,
            created_at=datetime.utcnow(),
        )
        model.validate()

        with self.uow:
            # If this is active, deactivate other models first
            if is_active:
                self._deactivate_all_models_except(model_id)
            self.uow.embedding_models.save(model)
            self.uow.commit()

        return model

    def register_version(
        self,
        model_id: str,
        version_string: str,
        configuration: Dict[str, Any],
    ) -> EmbeddingVersion:
        """Registers a configuration version for an embedding model."""
        with self.uow:
            model = self.uow.embedding_models.get_by_id(model_id)
            if not model:
                raise ValueError(f"Embedding model '{model_id}' does not exist.")

            version = EmbeddingVersion(
                id=uuid.uuid4(),
                model_id=model_id,
                version_string=version_string,
                configuration=configuration,
                registered_at=datetime.utcnow(),
            )
            version.validate()
            self.uow.embedding_versions.save(version)
            self.uow.commit()

        return version

    def activate_model(self, model_id: str) -> None:
        """Sets an embedding model as active and deactivates all others."""
        with self.uow:
            model = self.uow.embedding_models.get_by_id(model_id)
            if not model:
                raise ValueError(f"Embedding model '{model_id}' does not exist.")

            self._deactivate_all_models_except(model_id)
            model.is_active = True
            self.uow.embedding_models.save(model)
            self.uow.commit()

    def get_active_model(self) -> Optional[EmbeddingModel]:
        """Retrieves the currently active embedding model."""
        with self.uow:
            return self.uow.embedding_models.get_active_model()

    def get_version(self, model_id: str, version_string: str) -> Optional[EmbeddingVersion]:
        """Retrieves a specific version of a model."""
        with self.uow:
            return self.uow.embedding_versions.get_by_version(model_id, version_string)

    def generate_simulated_embedding(self, text: str) -> List[float]:
        """Generates a deterministic simulated/mock embedding vector based on the active model."""
        active_model = self.get_active_model()
        if not active_model:
            raise ValueError("No active embedding model is registered/selected.")

        # Generate a deterministic vector of size active_model.dimensions
        # We can seed a simple hash function or use the sum of char codes to fill the array
        import random
        seed = sum(ord(c) for c in text)
        rng = random.Random(seed)
        
        # Return a normalized vector (since many metrics assume unit length)
        raw_vector = [rng.gauss(0, 1) for _ in range(active_model.dimensions)]
        norm = sum(x * x for x in raw_vector) ** 0.5
        if norm > 0:
            return [x / norm for x in raw_vector]
        return [0.0] * active_model.dimensions

    def _deactivate_all_models_except(self, model_id: str) -> None:
        """Helper to deactivate all models except the given one."""
        # Since we don't have a list_all method in IEmbeddingModelRepository, 
        # we can query by id if needed or simply let the repository handle active uniqueness,
        # but to be safe we can use standard SQLAlchemy queries or rely on get_active_model
        active = self.uow.embedding_models.get_active_model()
        if active and active.id != model_id:
            active.is_active = False
            self.uow.embedding_models.save(active)
