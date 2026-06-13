"""Extractor for parsing OpenAPI and Swagger specifications."""

import os
import uuid
import json
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

class OpenAPIExtractor:
    """Parses OpenAPI specs (JSON or YAML) to extract API contracts."""
    
    def extract(self, file_path: str, content: str, repository_id: uuid.UUID) -> Tuple[List[CodeEntity], List[Relationship]]:
        entities = []
        relationships = []
        
        # Determine format
        data = None
        if file_path.endswith(".json") or content.strip().startswith("{"):
            try:
                data = json.loads(content)
            except Exception:
                pass
        else:
            try:
                data = yaml.safe_load(content)
            except Exception:
                pass
                
        if not isinstance(data, dict) or not ("openapi" in data or "swagger" in data or "paths" in data):
            return [], []
            
        # Extract main API Contract Entity
        info = data.get("info") or {}
        title = info.get("title", "API Contract")
        version = info.get("version", "1.0.0")
        
        api_seid = EntityIdentityService.generate_seid(
            entity_type=EntityType.API_CONTRACT,
            qualified_name=f"api:{title}",
            file_path=file_path,
            repo_id=RepositoryId(repository_id)
        )
        
        api_entity = CodeEntity(
            seid=api_seid,
            entity_type=EntityType.API_CONTRACT,
            name=title,
            qualified_name=f"api:{title}",
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
            metadata={
                "version": version,
                "layer": "SEMANTIC"
            }
        )
        entities.append(api_entity)
        
        # Extract operations
        paths = data.get("paths") or {}
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method, operation in path_item.items():
                if method.lower() not in ("get", "post", "put", "delete", "patch", "options", "head"):
                    continue
                if not isinstance(operation, dict):
                    continue
                    
                op_id = operation.get("operationId") or f"{method}:{path}"
                summary = operation.get("summary", "")
                
                op_seid = EntityIdentityService.generate_seid(
                    entity_type=EntityType.API_CONTRACT,
                    qualified_name=f"api:{title}:{method}:{path}",
                    file_path=file_path,
                    repo_id=RepositoryId(repository_id)
                )
                
                op_entity = CodeEntity(
                    seid=op_seid,
                    entity_type=EntityType.API_CONTRACT,
                    name=op_id,
                    qualified_name=f"api:{title}:{method}:{path}",
                    file_id=FileId(uuid.uuid4()),
                    repository_id=RepositoryId(repository_id),
                    parent_seid=api_seid,
                    language=SupportedLanguage.UNKNOWN,
                    location=CodeLocation(
                        file_path=file_path,
                        start_line=1,
                        end_line=1,
                        start_column=1,
                        end_column=1
                    ),
                    metadata={
                        "path": path,
                        "method": method,
                        "summary": summary,
                        "layer": "SEMANTIC"
                    }
                )
                entities.append(op_entity)
                
                # Relate operation to parent API contract
                relationships.append(Relationship(
                    id=uuid.uuid4(),
                    repository_id=RepositoryId(repository_id),
                    relationship_type=RelationshipType.CONTAINS,
                    source_seid=api_seid,
                    target_seid=op_seid,
                    confidence=1.0,
                    metadata={"layer": "SEMANTIC"}
                ))
                
        return entities, relationships
