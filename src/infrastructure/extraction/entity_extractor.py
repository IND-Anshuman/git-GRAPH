"""Service for extracting CodeEntity objects."""

from typing import List, Any
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.source_file import SourceFile
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.domain.services.identity_service import EntityIdentityService
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.strategies.python_strategy import PythonExtractionStrategy

class EntityExtractorService:
    """Extracts CodeEntity objects using language-specific strategies."""
    
    def __init__(self, registry: LanguageRegistry, identity_service: EntityIdentityService):
        self._registry = registry
        self._identity_service = identity_service
        self._strategies = {
            "PYTHON": PythonExtractionStrategy()
            # other languages would be added here
        }
        
    def extract(self, parsed_tree: Any, source_code: str, source_file: SourceFile, repository_id: RepositoryId) -> List[CodeEntity]:
        """Extracts code entities from a parsed AST.
        
        Args:
            parsed_tree: The tree-sitter AST
            source_code: The file's source code
            source_file: The domain SourceFile object
            repository_id: The repository ID
            
        Returns:
            List of domain CodeEntity objects
        """
        language_name = source_file.language.name
        strategy = self._strategies.get(language_name)
        
        if not strategy:
            return []
            
        module_name = source_file.file_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        raw_entities = strategy.extract_entities(parsed_tree, source_code, source_file.file_path, module_name)
        
        # We need two passes. Pass 1: create entities without parents to generate SEIDs.
        # Wait, if we use identity service, SEID depends on qualified name, which depends on parent.
        # We can build a simple parent hierarchy map first.
        
        domain_entities = []
        name_to_seid = {}
        
        for raw in raw_entities:
            # Reconstruct parent SEID if possible
            parent_seid = name_to_seid.get(raw.parent_name) if raw.parent_name else None
            
            # Simple fully qualified name computation
            q_name = self._identity_service.compute_qualified_name(
                entity_name=raw.name,
                parent_qname=raw.parent_name, # Approximation
                module_path=source_file.file_path
            )
            
            seid = self._identity_service.generate_seid(
                repository_id=repository_id,
                entity_type=raw.entity_type,
                qualified_name=q_name
            )
            
            name_to_seid[raw.name] = seid
            
            content_hash = self._identity_service.compute_content_hash(raw.source_text)
            
            entity = CodeEntity(
                seid=seid,
                entity_type=raw.entity_type,
                name=raw.name,
                qualified_name=q_name,
                file_id=source_file.id,
                repository_id=repository_id,
                parent_seid=parent_seid,
                language=source_file.language,
                location=CodeLocation(
                    file_path=source_file.file_path,
                    start_line=raw.start_line,
                    end_line=raw.end_line,
                    start_column=raw.start_column,
                    end_column=raw.end_column
                ),
                content_hash=content_hash,
                structural_fingerprint=None, # TBD by structural hasher
                source_text=raw.source_text,
                metadata=raw.metadata
            )
            domain_entities.append(entity)
            
        return domain_entities
