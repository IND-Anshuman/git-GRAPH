"""Service for resolving repository-level dependency graphs from project manifests."""

import os
import re
import json
import xml.etree.ElementTree as ET
import uuid
from typing import List, Dict, Any
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.entity_id import SEID
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.relationship import Relationship
from src.domain.enums.entity_type import EntityType
from src.domain.enums.relationship_type import RelationshipType
from src.domain.enums.graph_layer import GraphLayer
from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.code_location import CodeLocation
from src.application.semantic.dependency_graph.repository_dependency_graph import RepositoryDependencyGraph

class DependencyResolutionService:
    """Parses package manager manifests and builds semantic dependency models."""

    def resolve_dependencies(self, repository_id: uuid.UUID, local_path: str) -> RepositoryDependencyGraph:
        """Scan manifest files in repository local_path and construct RepositoryDependencyGraph."""
        graph = RepositoryDependencyGraph(repository_id=repository_id)
        
        # 1. package.json
        pkg_json_path = os.path.join(local_path, "package.json")
        if os.path.exists(pkg_json_path):
            self._parse_package_json(graph, pkg_json_path, repository_id)

        # 2. requirements.txt
        req_txt_path = os.path.join(local_path, "requirements.txt")
        if os.path.exists(req_txt_path):
            self._parse_requirements_txt(graph, req_txt_path, repository_id)

        # 3. pyproject.toml
        pyproj_toml_path = os.path.join(local_path, "pyproject.toml")
        if os.path.exists(pyproj_toml_path):
            self._parse_pyproject_toml(graph, pyproj_toml_path, repository_id)

        # 4. Cargo.toml
        cargo_toml_path = os.path.join(local_path, "Cargo.toml")
        if os.path.exists(cargo_toml_path):
            self._parse_cargo_toml(graph, cargo_toml_path, repository_id)

        # 5. composer.json
        composer_json_path = os.path.join(local_path, "composer.json")
        if os.path.exists(composer_json_path):
            self._parse_composer_json(graph, composer_json_path, repository_id)

        # 6. go.mod
        go_mod_path = os.path.join(local_path, "go.mod")
        if os.path.exists(go_mod_path):
            self._parse_go_mod(graph, go_mod_path, repository_id)

        # 7. pom.xml
        pom_xml_path = os.path.join(local_path, "pom.xml")
        if os.path.exists(pom_xml_path):
            self._parse_pom_xml(graph, pom_xml_path, repository_id)

        return graph

    def _create_dependency_entity(self, graph: RepositoryDependencyGraph, name: str, version: str, manifest_path: str, repo_id: uuid.UUID) -> CodeEntity:
        """Helper to create a CodeEntity for an external package dependency."""
        # Namespace namespace uuid for packages
        pkg_namespace = uuid.UUID("d39e3ba0-8a7c-4828-9717-d1a1b15c9ff8")
        seid_val = uuid.uuid5(pkg_namespace, f"pkg:{name}:{version}")
        
        # Check if already present in graph
        seid_str = str(seid_val)
        if seid_str in graph.nodes:
            return graph.nodes[seid_str]

        # Determine language/type
        entity = CodeEntity(
            seid=SEID(seid_val),
            entity_type=EntityType.EXTERNAL_PACKAGE,
            name=name,
            qualified_name=name,
            file_id=uuid.uuid4(),  # Manifest virtual file ID
            repository_id=RepositoryId(repo_id),
            parent_seid=None,
            language=SupportedLanguage.UNKNOWN,
            location=CodeLocation(
                file_path=os.path.basename(manifest_path),
                start_line=1,
                end_line=1,
                start_column=1,
                end_column=1
            ),
            metadata={
                "version": version,
                "is_external": True,
                "layer": "SEMANTIC"
            }
        )
        # Assign layer to CodeEntity metadata
        entity.metadata["layer"] = "SEMANTIC"
        graph.add_node(entity)
        return entity

    def _parse_package_json(self, graph: RepositoryDependencyGraph, path: str, repo_id: uuid.UUID) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            
            for name, ver in {**deps, **dev_deps}.items():
                self._create_dependency_entity(graph, name, ver, path, repo_id)
        except Exception:
            pass

    def _parse_requirements_txt(self, graph: RepositoryDependencyGraph, path: str, repo_id: uuid.UUID) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Match name==version or name>=version
                parts = re.split(r"==|>=|<=|>|<|~=", line)
                name = parts[0].strip()
                version = parts[1].strip() if len(parts) > 1 else "latest"
                self._create_dependency_entity(graph, name, version, path, repo_id)
        except Exception:
            pass

    def _parse_pyproject_toml(self, graph: RepositoryDependencyGraph, path: str, repo_id: uuid.UUID) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Simple regex parser for toml dependencies to avoid adding standard library toml requirement
            deps_section = re.search(r"\[tool\.poetry\.dependencies\](.*?)(\n\[|\Z)", content, re.DOTALL)
            if deps_section:
                for line in deps_section.group(1).splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    parts = line.split("=")
                    name = parts[0].strip().strip('"').strip("'")
                    version = parts[1].strip().strip('"').strip("'")
                    if name.lower() != "python":
                        self._create_dependency_entity(graph, name, version, path, repo_id)
        except Exception:
            pass

    def _parse_cargo_toml(self, graph: RepositoryDependencyGraph, path: str, repo_id: uuid.UUID) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            deps_section = re.search(r"\[dependencies\](.*?)(\n\[|\Z)", content, re.DOTALL)
            if deps_section:
                for line in deps_section.group(1).splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    parts = line.split("=")
                    name = parts[0].strip().strip('"').strip("'")
                    version = parts[1].strip().strip('"').strip("'")
                    self._create_dependency_entity(graph, name, version, path, repo_id)
        except Exception:
            pass

    def _parse_composer_json(self, graph: RepositoryDependencyGraph, path: str, repo_id: uuid.UUID) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            deps = data.get("require", {})
            for name, ver in deps.items():
                if name.lower() != "php":
                    self._create_dependency_entity(graph, name, ver, path, repo_id)
        except Exception:
            pass

    def _parse_go_mod(self, graph: RepositoryDependencyGraph, path: str, repo_id: uuid.UUID) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line.startswith("require") or line.startswith("("):
                    # check lines inside block or single require
                    match = re.search(r"require\s+([^\s]+)\s+([^\s]+)", line)
                    if match:
                        self._create_dependency_entity(graph, match.group(1), match.group(2), path, repo_id)
                    else:
                        match_inner = re.search(r"([^\s]+)\s+([^\s\(\)]+)", line)
                        if match_inner and not line.startswith("require") and not line.startswith("go "):
                            self._create_dependency_entity(graph, match_inner.group(1), match_inner.group(2), path, repo_id)
        except Exception:
            pass

    def _parse_pom_xml(self, graph: RepositoryDependencyGraph, path: str, repo_id: uuid.UUID) -> None:
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            # Handle XML namespaces
            ns = {"m": root.tag.split("}")[0].strip("{")} if "}" in root.tag else {}
            
            query = ".//m:dependency" if ns else ".//dependency"
            for dep in root.findall(query, ns):
                g_id = dep.find("m:groupId", ns) if ns else dep.find("groupId")
                a_id = dep.find("m:artifactId", ns) if ns else dep.find("artifactId")
                ver = dep.find("m:version", ns) if ns else dep.find("version")
                
                if g_id is not None and a_id is not None:
                    name = f"{g_id.text}:{a_id.text}"
                    version = ver.text if ver is not None else "latest"
                    self._create_dependency_entity(graph, name, version, path, repo_id)
        except Exception:
            pass
