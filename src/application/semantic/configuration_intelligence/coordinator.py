"""Coordinator for all configuration intelligence extractors."""

import os
import uuid
from typing import List, Dict, Any, Tuple
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.relationship import Relationship
from src.application.semantic.configuration_intelligence.docker_extractor import DockerExtractor
from src.application.semantic.configuration_intelligence.k8s_extractor import KubernetesExtractor
from src.application.semantic.configuration_intelligence.terraform_extractor import TerraformExtractor
from src.application.semantic.configuration_intelligence.openapi_extractor import OpenAPIExtractor
from src.application.semantic.configuration_intelligence.protobuf_extractor import ProtobufExtractor

class ConfigurationIntelligenceService:
    """Coordinates various configuration intelligence extractors to parse repository configuration files."""
    
    def __init__(self) -> None:
        self.docker_extractor = DockerExtractor()
        self.k8s_extractor = KubernetesExtractor()
        self.terraform_extractor = TerraformExtractor()
        self.openapi_extractor = OpenAPIExtractor()
        self.protobuf_extractor = ProtobufExtractor()
        
    def scan_repository(self, local_path: str, repository_id: uuid.UUID) -> Tuple[List[CodeEntity], List[Relationship]]:
        all_entities = []
        all_relationships = []
        
        for root, _, files in os.walk(local_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, local_path).replace("\\", "/")
                
                # Check for Dockerfiles
                if file.lower() == "dockerfile" or file.lower().startswith("dockerfile."):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        ents, rels = self.docker_extractor.extract(rel_path, content, repository_id)
                        all_entities.extend(ents)
                        all_relationships.extend(rels)
                    except Exception:
                        pass
                
                # Check for Kubernetes yaml manifests
                elif file.endswith(".yaml") or file.endswith(".yml"):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        # Verify it has apiVersion & kind to avoid running on regular yaml config/yaml behavior rules
                        if "apiVersion" in content and "kind" in content:
                            ents, rels = self.k8s_extractor.extract(rel_path, content, repository_id)
                            all_entities.extend(ents)
                            all_relationships.extend(rels)
                        # Could be OpenAPI YAML
                        elif "openapi:" in content or "swagger:" in content or "paths:" in content:
                            ents, rels = self.openapi_extractor.extract(rel_path, content, repository_id)
                            all_entities.extend(ents)
                            all_relationships.extend(rels)
                    except Exception:
                        pass
                        
                # Check for Terraform files
                elif file.endswith(".tf"):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        ents, rels = self.terraform_extractor.extract(rel_path, content, repository_id)
                        all_entities.extend(ents)
                        all_relationships.extend(rels)
                    except Exception:
                        pass
                        
                # Check for OpenAPI json spec
                elif file.endswith(".json") and ("openapi" in file.lower() or "swagger" in file.lower()):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        ents, rels = self.openapi_extractor.extract(rel_path, content, repository_id)
                        all_entities.extend(ents)
                        all_relationships.extend(rels)
                    except Exception:
                        pass
                        
                # Check for Protobuf files
                elif file.endswith(".proto"):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        ents, rels = self.protobuf_extractor.extract(rel_path, content, repository_id)
                        all_entities.extend(ents)
                        all_relationships.extend(rels)
                    except Exception:
                        pass
                        
        return all_entities, all_relationships
