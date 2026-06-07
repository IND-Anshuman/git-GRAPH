"""Application service managing the ontology and pattern registry catalog."""

import os
from typing import Callable, List, Optional
import yaml

from src.domain.entities.behavior_pattern import BehaviorPattern
from src.domain.entities.ontology_node import OntologyNode
from src.application.ports.unit_of_work import IUnitOfWork
from src.infrastructure.logic.ontology_loader import OntologyLoader
from src.infrastructure.logic.pattern_registry import PatternRegistry
from src.domain.exceptions import OntologyLoadException


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
        self.detect_node_cycles(nodes)
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

    def detect_node_cycles(self, nodes: List[OntologyNode]) -> None:
        """Detect parent-child cycles in the loaded OntologyNodes."""
        adj = {}
        node_ids = {n.id for n in nodes}
        for node in nodes:
            if node.parent_id:
                if node.parent_id not in adj:
                    adj[node.parent_id] = []
                adj[node.parent_id].append(node.id)

        visited = set()
        visiting = set()

        def dfs(node_id):
            visiting.add(node_id)
            for neighbor in adj.get(node_id, []):
                if neighbor in visiting:
                    raise OntologyLoadException(f"Ontology cycle detected involving node: {node_id} -> {neighbor}")
                if neighbor not in visited:
                    dfs(neighbor)
            visiting.remove(node_id)
            visited.add(node_id)

        for node_id in node_ids:
            if node_id not in visited:
                dfs(node_id)

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


class ConceptOntologyRegistry:
    """Service to load, validate, check cycles, and lookup concepts from concepts.yaml."""

    def __init__(self, yaml_path: str = None) -> None:
        if yaml_path is None:
            # Resolve relative to project root or use a standard path
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            yaml_path = os.path.join(base_dir, "infrastructure", "ontology", "concepts.yaml")
        self.yaml_path = yaml_path
        self._domains = []
        self._concepts = {}
        self._pattern_to_concept = {}
        self.load_ontology()

    def load_ontology(self) -> None:
        """Load the concept ontology YAML file."""
        if not os.path.exists(self.yaml_path):
            raise OntologyLoadException(f"Concept ontology file does not exist: {self.yaml_path}")
        try:
            with open(self.yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise OntologyLoadException(f"Failed to read/parse concept ontology YAML: {e}")

        self.validate_ontology(data)
        self.detect_cycles()

    def validate_ontology(self, data: dict) -> None:
        """Validate YAML schema structures and parent-child loops."""
        if not data:
            raise OntologyLoadException("Concept ontology data is empty.")
        
        schema_version = data.get("schema_version")
        if not schema_version:
            raise OntologyLoadException("Missing 'schema_version' in concept ontology.")
        
        domains_list = data.get("domains", [])
        if not isinstance(domains_list, list):
            raise OntologyLoadException("'domains' must be a list in concept ontology.")

        for domain in domains_list:
            domain_id = domain.get("id")
            domain_name = domain.get("name")
            if not domain_id or not domain_name:
                raise OntologyLoadException("Domain must have both 'id' and 'name' in concept ontology.")
            
            concepts_list = domain.get("concepts", [])
            if not isinstance(concepts_list, list):
                raise OntologyLoadException(f"'concepts' must be a list under domain {domain_id}.")

            for concept in concepts_list:
                concept_id = concept.get("id")
                concept_name = concept.get("name")
                if not concept_id or not concept_name:
                    raise OntologyLoadException(f"Concept must have both 'id' and 'name' under domain {domain_id}.")
                
                if concept_id in self._concepts:
                    raise OntologyLoadException(f"Duplicate concept ID detected: {concept_id}")
                
                required = concept.get("required_patterns", [])
                optional = concept.get("optional_patterns", [])
                if not isinstance(required, list) or not isinstance(optional, list):
                    raise OntologyLoadException(f"Patterns must be lists in concept {concept_id}.")

                self._concepts[concept_id] = {
                    "id": concept_id,
                    "name": concept_name,
                    "description": concept.get("description", ""),
                    "domain_id": domain_id,
                    "parent_id": concept.get("parent_id"),
                    "required_patterns": required,
                    "optional_patterns": optional,
                    "min_base_confidence": float(concept.get("min_base_confidence", 0.70)),
                }

                for pattern in required + optional:
                    self._pattern_to_concept[pattern] = concept_id

            self._domains.append({
                "id": domain_id,
                "name": domain_name,
                "description": domain.get("description", ""),
            })

    def detect_cycles(self) -> None:
        """Detect cycles in parent-child relationships among concepts."""
        adj = {}
        for cid, concept in self._concepts.items():
            parent = concept.get("parent_id")
            if parent:
                if parent not in adj:
                    adj[parent] = []
                adj[parent].append(cid)

        visited = set()
        visiting = set()

        def dfs(node):
            visiting.add(node)
            for neighbor in adj.get(node, []):
                if neighbor in visiting:
                    raise OntologyLoadException(f"Ontology cycle detected involving: {node} -> {neighbor}")
                if neighbor not in visited:
                    dfs(neighbor)
            visiting.remove(node)
            visited.add(node)

        for node in self._concepts:
            if node not in visited:
                dfs(node)

    def get_concept(self, concept_id: str) -> Optional[dict]:
        """Look up a concept definition by its unique ID."""
        return self._concepts.get(concept_id)

    def get_concept_by_pattern(self, pattern_id: str) -> Optional[str]:
        """Look up which concept ID matches the given pattern ID."""
        return self._pattern_to_concept.get(pattern_id)

    def get_all_concepts(self) -> List[dict]:
        """Retrieve list of all parsed concept definitions."""
        return list(self._concepts.values())

    def get_all_domains(self) -> List[dict]:
        """Retrieve list of all ontology domains."""
        return self._domains
