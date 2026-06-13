"""Extractor for parsing Kubernetes manifests."""

import os
import uuid
import yaml
from typing import List, Dict, Any, Tuple
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.relationship import Relationship
from src.domain.enums.entity_type import EntityType
from src.domain.enums.relationship_type import RelationshipType
from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.domain.services.identity_service import EntityIdentityService

class KubernetesExtractor:
    """Parses Kubernetes manifests to extract deployment and service metadata."""
    
    def extract(self, file_path: str, content: str, repository_id: uuid.UUID) -> Tuple[List[CodeEntity], List[Relationship]]:
        entities = []
        relationships = []
        
        # Check if it looks like YAML and has K8s fields
        if not ("apiVersion" in content and "kind" in content):
            return [], []
            
        try:
            # Load all YAML documents in the file
            docs = yaml.safe_load_all(content)
            for doc in docs:
                if not doc or not isinstance(doc, dict):
                    continue
                
                kind = doc.get("kind")
                metadata_section = doc.get("metadata") or {}
                name = metadata_section.get("name")
                if not kind or not name:
                    continue
                    
                namespace = metadata_section.get("namespace", "default")
                
                if kind in ("Deployment", "StatefulSet", "DaemonSet", "Pod"):
                    entity_type = EntityType.DEPLOYMENT
                elif kind in ("Service", "Ingress"):
                    entity_type = EntityType.SERVICE_DEFINITION
                else:
                    entity_type = EntityType.CONFIGURATION_FILE
                
                seid = EntityIdentityService.generate_seid(
                    entity_type=entity_type,
                    qualified_name=f"{namespace}:{kind}:{name}",
                    file_path=file_path,
                    repo_id=RepositoryId(repository_id)
                )
                
                # Extract spec info
                spec = doc.get("spec") or {}
                replicas = spec.get("replicas", 1) if kind in ("Deployment", "StatefulSet") else 1
                
                # Parse containers
                containers_info = []
                template = spec.get("template") or {}
                template_spec = template.get("spec") or spec
                containers = template_spec.get("containers") or []
                for c in containers:
                    c_name = c.get("name")
                    c_image = c.get("image")
                    c_ports = [p.get("containerPort") for p in c.get("ports") or [] if p.get("containerPort")]
                    containers_info.append({
                        "name": c_name,
                        "image": c_image,
                        "ports": c_ports
                    })
                    
                # Parse service ports
                service_ports = []
                if kind == "Service":
                    ports = spec.get("ports") or []
                    for p in ports:
                        service_ports.append({
                            "port": p.get("port"),
                            "targetPort": p.get("targetPort"),
                            "protocol": p.get("protocol", "TCP")
                        })
                
                metadata = {
                    "kind": kind,
                    "name": name,
                    "namespace": namespace,
                    "replicas": replicas,
                    "containers": containers_info,
                    "ports": service_ports,
                    "layer": "SEMANTIC"
                }
                
                entity = CodeEntity(
                    seid=seid,
                    entity_type=entity_type,
                    name=name,
                    qualified_name=f"{namespace}:{kind}:{name}",
                    file_id=FileId(uuid.uuid4()),
                    repository_id=RepositoryId(repository_id),
                    parent_seid=None,
                    language=SupportedLanguage.UNKNOWN,
                    location=CodeLocation(
                        file_path=file_path,
                        start_line=1,
                        end_line=1,
                        start_column=1,
                        end_column=1
                    ),
                    content_hash=EntityIdentityService.compute_content_hash(content),
                    source_text=content,
                    metadata=metadata
                )
                
                entities.append(entity)
                
        except Exception:
            pass
            
        return entities, relationships
