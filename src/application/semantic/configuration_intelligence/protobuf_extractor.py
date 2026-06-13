"""Extractor for parsing Protobuf definition files."""

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

class ProtobufExtractor:
    """Parses Protobuf files to extract message and service contracts."""
    
    def extract(self, file_path: str, content: str, repository_id: uuid.UUID) -> Tuple[List[CodeEntity], List[Relationship]]:
        entities = []
        relationships = []
        
        # Regexes
        package_pattern = re.compile(r'package\s+([a-zA-Z0-9_\.]+);')
        message_pattern = re.compile(r'message\s+([a-zA-Z0-9_]+)\s*\{')
        service_pattern = re.compile(r'service\s+([a-zA-Z0-9_]+)\s*\{')
        rpc_pattern = re.compile(r'rpc\s+([a-zA-Z0-9_]+)\s*\(\s*([a-zA-Z0-9_\.]+)\s*\)\s*returns\s*\(\s*([a-zA-Z0-9_\.]+)\s*\)')
        
        package_name = "default"
        pkg_match = package_pattern.search(content)
        if pkg_match:
            package_name = pkg_match.group(1)
            
        lines = content.splitlines()
        current_service_seid = None
        
        for i, line in enumerate(lines):
            line_str = line.strip()
            
            # Check message definition
            msg_match = message_pattern.match(line_str)
            if msg_match:
                msg_name = msg_match.group(1)
                q_name = f"{package_name}.{msg_name}"
                
                seid = EntityIdentityService.generate_seid(
                    entity_type=EntityType.MESSAGE_CONTRACT,
                    qualified_name=q_name,
                    file_path=file_path,
                    repo_id=RepositoryId(repository_id)
                )
                
                entity = CodeEntity(
                    seid=seid,
                    entity_type=EntityType.MESSAGE_CONTRACT,
                    name=msg_name,
                    qualified_name=q_name,
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
                    metadata={"package": package_name, "layer": "SEMANTIC"}
                )
                entities.append(entity)
                
            # Check service definition
            srv_match = service_pattern.match(line_str)
            if srv_match:
                srv_name = srv_match.group(1)
                q_name = f"{package_name}.{srv_name}"
                
                current_service_seid = EntityIdentityService.generate_seid(
                    entity_type=EntityType.SERVICE_DEFINITION,
                    qualified_name=q_name,
                    file_path=file_path,
                    repo_id=RepositoryId(repository_id)
                )
                
                entity = CodeEntity(
                    seid=current_service_seid,
                    entity_type=EntityType.SERVICE_DEFINITION,
                    name=srv_name,
                    qualified_name=q_name,
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
                    metadata={"package": package_name, "layer": "SEMANTIC"}
                )
                entities.append(entity)
                
            # Check RPC method definition inside service
            rpc_match = rpc_pattern.search(line_str)
            if rpc_match and current_service_seid:
                rpc_name = rpc_match.group(1)
                req_type = rpc_match.group(2)
                res_type = rpc_match.group(3)
                
                rpc_qname = f"{package_name}.{rpc_name}"
                rpc_seid = EntityIdentityService.generate_seid(
                    entity_type=EntityType.API_CONTRACT,
                    qualified_name=rpc_qname,
                    file_path=file_path,
                    repo_id=RepositoryId(repository_id)
                )
                
                entity = CodeEntity(
                    seid=rpc_seid,
                    entity_type=EntityType.API_CONTRACT,
                    name=rpc_name,
                    qualified_name=rpc_qname,
                    file_id=FileId(uuid.uuid4()),
                    repository_id=RepositoryId(repository_id),
                    parent_seid=current_service_seid,
                    language=SupportedLanguage.UNKNOWN,
                    location=CodeLocation(
                        file_path=file_path,
                        start_line=i + 1,
                        end_line=i + 1,
                        start_column=1,
                        end_column=1
                    ),
                    metadata={
                        "request_type": req_type,
                        "response_type": res_type,
                        "layer": "SEMANTIC"
                    }
                )
                entities.append(entity)
                
                # Add relationship: Service CONTAINS RPC
                relationships.append(Relationship(
                    id=uuid.uuid4(),
                    repository_id=RepositoryId(repository_id),
                    relationship_type=RelationshipType.CONTAINS,
                    source_seid=current_service_seid,
                    target_seid=rpc_seid,
                    confidence=1.0,
                    metadata={"layer": "SEMANTIC"}
                ))
                
        return entities, relationships
