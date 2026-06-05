"""Application service managing the ontology and pattern registry catalog."""

from typing import Callable, List, Optional

from src.domain.entities.behavior_pattern import BehaviorPattern
from src.domain.entities.ontology_node import OntologyNode
from src.application.ports.unit_of_work import IUnitOfWork
from src.infrastructure.logic.ontology_loader import OntologyLoader
from src.infrastructure.logic.pattern_registry import PatternRegistry


class OntologyRegistryService:
    """Service to load, store, reload, and query behavioral ontology and patterns."""

    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        loader: OntologyLoader,
        in_memory_patterns: PatternRegistry,
    ) -> None:
        self._uow_factory = uow_factory
        self._loader = loader
        self._in_memory_patterns = in_memory_patterns

    def load_ontology_and_patterns(
        self, ontology_dir: str, patterns_dir: str
    ) -> None:
        """
        Load nodes and patterns from YAML directories, validate them, and persist to database.

        Old nodes and patterns are cleared before saving the new ones.
        """
        # 1. Load from files
        nodes = self._loader.load_from_directory(ontology_dir)
        patterns = self._in_memory_patterns.load_from_directory(patterns_dir)

        # 2. Clear and Save to database using Unit of Work transaction
        with self._uow_factory() as uow:
            uow.behavior_patterns.delete_all()
            uow.ontology_nodes.delete_all()

            uow.ontology_nodes.save_batch(nodes)
            uow.behavior_patterns.save_batch(patterns)
            uow.commit()

        # 3. Register in in-memory pattern registry for active scan matching
        self._in_memory_patterns.clear()
        self._in_memory_patterns.register_patterns(patterns)

    def initialize_registry(self) -> None:
        """Load database patterns into the in-memory registry on startup."""
        with self._uow_factory() as uow:
            patterns = uow.behavior_patterns.list_active()
        self._in_memory_patterns.clear()
        self._in_memory_patterns.register_patterns(patterns)

    def get_all_nodes(self) -> List[OntologyNode]:
        """Query all ontology nodes from the database."""
        with self._uow_factory() as uow:
            return uow.ontology_nodes.list_all()

    def get_node_by_id(self, node_id: str) -> Optional[OntologyNode]:
        """Query a single ontology node by its ID."""
        with self._uow_factory() as uow:
            return uow.ontology_nodes.get_by_id(node_id)

    def get_all_patterns(self) -> List[BehaviorPattern]:
        """Query all behavior patterns from the database."""
        with self._uow_factory() as uow:
            return uow.behavior_patterns.list_active()

    def get_pattern_by_id(self, pattern_id: str) -> Optional[BehaviorPattern]:
        """Query a single behavior pattern by its pattern ID."""
        with self._uow_factory() as uow:
            return uow.behavior_patterns.get_by_pattern_id(pattern_id)
