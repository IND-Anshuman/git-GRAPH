"""Service for loading and validating ontology nodes from YAML files."""

import os
from datetime import datetime
from typing import Any, List
import yaml

from src.domain.entities.ontology_node import OntologyNode
from src.domain.exceptions import OntologyLoadException


class OntologyLoader:
    """Loads and validates OntologyNode entities from a directory of YAML files."""

    def load_from_directory(self, directory_path: str) -> List[OntologyNode]:
        """
        Load all ontology YAML files from the specified directory.

        Args:
            directory_path: Absolute path to the directory containing ontology YAML files.

        Returns:
            A flat list of all parsed OntologyNode entities.

        Raises:
            OntologyLoadException: If loading or validation fails.
        """
        if not os.path.isdir(directory_path):
            raise OntologyLoadException(
                f"Ontology directory does not exist: {directory_path}"
            )

        nodes = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                filepath = os.path.join(directory_path, filename)
                nodes.extend(self.load_from_file(filepath))

        return nodes

    def load_from_file(self, file_path: str) -> List[OntologyNode]:
        """
        Load and validate ontology nodes from a single YAML file.

        Args:
            file_path: Absolute path to the ontology YAML file.

        Returns:
            A list of OntologyNode entities.

        Raises:
            OntologyLoadException: If parsing or validation fails.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise OntologyLoadException(
                f"Failed to read/parse YAML in {file_path}: {e}"
            ) from e

        if not data:
            return []

        # Validate top-level schema
        schema_version = data.get("schema_version")
        ontology_version = data.get("ontology_version")
        domain = data.get("domain")

        if not domain:
            raise OntologyLoadException(
                f"Missing 'domain' field in ontology file: {file_path}"
            )
        if not ontology_version:
            raise OntologyLoadException(
                f"Missing 'ontology_version' field in ontology file: {file_path}"
            )

        nodes: List[OntologyNode] = []

        raw_nodes = data.get("nodes", [])
        if not isinstance(raw_nodes, list):
            raise OntologyLoadException(
                f"'nodes' must be a list in ontology file: {file_path}"
            )

        def parse_node(node_data: dict[str, Any], parent_id: str | None = None) -> None:
            node_id = node_data.get("id")
            name = node_data.get("name")
            description = node_data.get("description", "")
            is_leaf = node_data.get("is_leaf", False)

            if not node_id:
                raise OntologyLoadException(
                    f"Ontology node missing 'id' in: {file_path}"
                )
            if not name:
                raise OntologyLoadException(
                    f"Ontology node {node_id} missing 'name' in: {file_path}"
                )

            # Explicitly specified parent_id or inherited
            resolved_parent = node_data.get("parent_id", parent_id)

            node = OntologyNode(
                id=node_id,
                name=name,
                parent_id=resolved_parent,
                domain=domain,
                description=description,
                ontology_version=ontology_version,
                is_leaf=is_leaf,
                metadata={
                    "schema_version": schema_version,
                    "source_file": os.path.basename(file_path),
                },
                loaded_at=datetime.utcnow(),
            )
            nodes.append(node)

            # Process nested children recursively
            children = node_data.get("children", [])
            for child_data in children:
                parse_node(child_data, parent_id=node_id)

        for raw_node in raw_nodes:
            parse_node(raw_node)

        return nodes
