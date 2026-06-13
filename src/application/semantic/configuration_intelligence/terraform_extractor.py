"""Extractor for parsing Terraform configurations."""

import os
import uuid
import re
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

class TerraformExtractor:
    """Parses Terraform files to extract infrastructure resource metadata."""
    
    def extract(self, file_path: str, content: str, repository_id: uuid.UUID) -> Tuple[List[CodeEntity], List[Relationship]]:
        entities = []
        relationships = []
        
        # Simple regex parsing for resources, providers, modules
        resource_pattern = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{')
        provider_pattern = re.compile(r'provider\s+"([^"]+)"\s*\{')
        module_pattern = re.compile(r'module\s+"([^"]+)"\s*\{')
        
        lines = content.splitlines()
        for i, line in enumerate(lines):
            # Check for resource
            res_match = resource_pattern.match(line.strip())
            if res_match:
                res_type = res_match.group(1)
                res_name = res_match.group(2)
                qualified_name = f"{res_type}.{res_name}"
                
                seid = EntityIdentityService.generate_seid(
                    entity_type=EntityType.DEPLOYMENT, # Represents deployed resources
                    qualified_name=qualified_name,
                    file_path=file_path,
                    repo_id=RepositoryId(repository_id)
                )
                
                metadata = {
                    "resource_type": res_type,
                    "resource_name": res_name,
                    "layer": "SEMANTIC"
                }
                
                entity = CodeEntity(
                    seid=seid,
                    entity_type=EntityType.DEPLOYMENT,
                    name=res_name,
                    qualified_name=qualified_name,
                    file_id=FileId(uuid.uuid4()),
                    repository_id=RepositoryId(repository_id),
                    parent_seid=None,
                    language=SupportedLanguage.UNKNOWN,
                    location=CodeLocation(
                        file_path=file_path,
                        start_line=i + 1,
                        end_line=i + 1,
                        start_column=1,
                        end_column=1
                    ),
                    content_hash=EntityIdentityService.compute_content_hash(line),
                    source_text=line,
                    metadata=metadata
                )
                entities.append(entity)
                
            # Check for module
            mod_match = module_pattern.match(line.strip())
            if mod_match:
                mod_name = mod_match.group(1)
                seid = EntityIdentityService.generate_seid(
                    entity_type=EntityType.CONFIGURATION_FILE,
                    qualified_name=f"module.{mod_name}",
                    file_path=file_path,
                    repo_id=RepositoryId(repository_id)
                )
                
                entity = CodeEntity(
                    seid=seid,
                    entity_type=EntityType.CONFIGURATION_FILE,
                    name=mod_name,
                    qualified_name=f"module.{mod_name}",
                    file_id=FileId(uuid.uuid4()),
                    repository_id=RepositoryId(repository_id),
                    parent_seid=None,
                    language=SupportedLanguage.UNKNOWN,
                    location=CodeLocation(
                        file_path=file_path,
                        start_line=i + 1,
                        end_line=i + 1,
                        start_column=1,
                        end_column=1
                    ),
                    metadata={"module_name": mod_name, "layer": "SEMANTIC"}
                )
                entities.append(entity)
                
        return entities, relationships
