"""Extractor for parsing Dockerfiles."""

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

class DockerExtractor:
    """Parses Dockerfiles to extract container and configuration metadata."""
    
    def extract(self, file_path: str, content: str, repository_id: uuid.UUID) -> Tuple[List[CodeEntity], List[Relationship]]:
        entities = []
        relationships = []
        
        # Determine container name based on directory or filename
        rel_path = file_path
        name = os.path.basename(file_path)
        if name.lower() == "dockerfile":
            # use parent folder name
            parent = os.path.basename(os.path.dirname(file_path))
            name = f"dockerfile-{parent}" if parent else "dockerfile"
        
        # Parse content
        base_image = "scratch"
        exposed_ports = []
        env_vars = {}
        
        lines = content.splitlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            
            # FROM base_image
            from_match = re.match(r"^FROM\s+([^\s]+)", line, re.IGNORECASE)
            if from_match:
                base_image = from_match.group(1)
                
            # EXPOSE ports
            expose_match = re.match(r"^EXPOSE\s+(.+)", line, re.IGNORECASE)
            if expose_match:
                ports = expose_match.group(1).split()
                exposed_ports.extend(ports)
                
            # ENV key value
            env_match = re.match(r"^ENV\s+([^\s=]+)[=\s]+(.*)", line, re.IGNORECASE)
            if env_match:
                key = env_match.group(1).strip()
                val = env_match.group(2).strip()
                env_vars[key] = val
                
        # Generate CodeEntity
        seid = EntityIdentityService.generate_seid(
            entity_type=EntityType.CONTAINER,
            qualified_name=name,
            file_path=rel_path,
            repo_id=RepositoryId(repository_id)
        )
        
        metadata = {
            "base_image": base_image,
            "exposed_ports": exposed_ports,
            "env_vars": env_vars,
            "layer": "SEMANTIC"
        }
        
        entity = CodeEntity(
            seid=seid,
            entity_type=EntityType.CONTAINER,
            name=name,
            qualified_name=name,
            file_id=FileId(uuid.uuid4()),
            repository_id=RepositoryId(repository_id),
            parent_seid=None,
            language=SupportedLanguage.UNKNOWN,
            location=CodeLocation(
                file_path=rel_path,
                start_line=1,
                end_line=max(1, len(lines)),
                start_column=1,
                end_column=1
            ),
            content_hash=EntityIdentityService.compute_content_hash(content),
            source_text=content,
            metadata=metadata
        )
        
        entities.append(entity)
        return entities, relationships
