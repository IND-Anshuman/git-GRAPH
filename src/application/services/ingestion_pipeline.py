from dataclasses import dataclass
from typing import Any
import os
import uuid
from src.domain.entities import RepositoryEntity, SourceFile, CodeEntity, Relationship
from src.domain.enums import AnalysisStatus, SupportedLanguage
from src.application.ports.git_port import IGitAdapter
from src.application.ports.file_scanner_port import IFileScanner
from src.application.ports.parser_port import IParser
import logging

logger = logging.getLogger(__name__)

@dataclass
class PipelineResult:
    files: list[SourceFile]
    entities: list[CodeEntity]
    relationships: list[Relationship]
    errors: list[str]

class IngestionPipeline:
    def __init__(
        self,
        git_adapter: IGitAdapter,
        file_scanner: IFileScanner,
        parser: IParser,
        entity_extractor: Any,
        relationship_extractor: Any,
        identity_service: Any
    ):
        self.git_adapter = git_adapter
        self.file_scanner = file_scanner
        self.parser = parser
        self.entity_extractor = entity_extractor
        self.relationship_extractor = relationship_extractor
        self.identity_service = identity_service

    def run(self, repository: RepositoryEntity, storage_root: str) -> PipelineResult:
        result = PipelineResult(files=[], entities=[], relationships=[], errors=[])
        
        try:
            target_dir = os.path.join(storage_root, str(repository.id))
            repository.status = AnalysisStatus.CLONING
            local_path = self.git_adapter.clone_repository(repository.url, repository.default_branch, target_dir)
            repository.local_path = local_path

            repository.status = AnalysisStatus.SCANNING
            scanned_files = self.file_scanner.scan_repository(local_path)
            
            repository.status = AnalysisStatus.PARSING
            
            for scanned in scanned_files:
                try:
                    with open(scanned.absolute_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    content_hash = self.identity_service.compute_content_hash(content)
                    
                    from src.domain.value_objects.file_id import FileId
                    source_file = SourceFile(
                        id=FileId(uuid.uuid4()),
                        repository_id=repository.id,
                        file_path=scanned.path,
                        language=scanned.language,
                        content_hash=content_hash,
                        line_count=len(content.splitlines()),
                        size_bytes=scanned.size_bytes
                    )
                    result.files.append(source_file)
                    
                    parse_result = self.parser.parse_file(scanned.absolute_path, content, scanned.language)
                    if parse_result.errors:
                        result.errors.extend(parse_result.errors)
                        
                    file_entities = self.entity_extractor.extract(
                        parsed_tree=parse_result.tree,
                        source_code=content,
                        source_file=source_file,
                        repository_id=repository.id
                    )
                    result.entities.extend(file_entities)
                    
                    file_relationships = self.relationship_extractor.extract(
                        parsed_tree=parse_result.tree,
                        source_code=content,
                        entities=file_entities,
                        source_file=source_file
                    )
                    result.relationships.extend(file_relationships)
                    
                except Exception as ex:
                    logger.error(f"Error processing file {scanned.path}: {ex}")
                    result.errors.append(f"Error in {scanned.path}: {ex}")

            repository.status = AnalysisStatus.EXTRACTING
            
            return result
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            result.errors.append(str(e))
            return result
