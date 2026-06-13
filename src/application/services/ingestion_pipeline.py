"""Ingestion Pipeline for orchestrating SEEE, parsing, and Configuration Intelligence."""

import os
import uuid
import logging
import dataclasses
from enum import Enum
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, List, Dict

from src.domain.entities import RepositoryEntity, SourceFile, CodeEntity, Relationship
from src.domain.enums import AnalysisStatus, SupportedLanguage
from src.application.ports.git_port import IGitAdapter
from src.application.ports.file_scanner_port import IFileScanner
from src.application.ports.parser_port import IParser
from src.application.semantic.configuration_intelligence.coordinator import ConfigurationIntelligenceService

logger = logging.getLogger(__name__)

def to_json_ready(obj: Any) -> Any:
    """Recursively converts custom dataclasses, enums, UUIDs and datetimes to JSON-safe structures."""
    if isinstance(obj, list):
        return [to_json_ready(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_json_ready(v) for k, v in obj.items()}
    if dataclasses.is_dataclass(obj):
        return to_json_ready(dataclasses.asdict(obj))
    if isinstance(obj, Enum):
        return obj.name
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

@dataclass
class PipelineResult:
    files: list[SourceFile]
    entities: list[CodeEntity]
    relationships: list[Relationship]
    errors: list[str]
    seee_evidences: list[Any] = field(default_factory=list)
    compiler_outputs: list[Any] = field(default_factory=list)

class IngestionPipeline:
    """Orchestrates source file scanning, parsing, semantic evidence extraction (SEEE), and configuration intelligence."""
    
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
        self.config_intel_service = ConfigurationIntelligenceService()

    def run(self, repository: RepositoryEntity, storage_root: str) -> PipelineResult:
        result = PipelineResult(files=[], entities=[], relationships=[], errors=[])
        
        try:
            target_dir = os.path.join(storage_root, str(repository.id))
            repository.status = AnalysisStatus.CLONING
            local_path = self.git_adapter.clone_repository(repository.url, repository.default_branch, target_dir)
            repository.local_path = local_path

            # Get current commit hash
            commit_hash = "HEAD"
            try:
                commit_hash = self.git_adapter.get_current_commit_hash(local_path)
            except Exception as git_err:
                logger.warning(f"Could not retrieve HEAD commit hash: {git_err}")

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
                        
                    file_entities, ext_result = self.entity_extractor.extract(
                        parsed_tree=parse_result.tree,
                        source_code=content,
                        source_file=source_file,
                        repository_id=repository.id
                    )
                    
                    # Update all entities to have the structural layer
                    for e in file_entities:
                        e.metadata["layer"] = "STRUCTURAL"
                    result.entities.extend(file_entities)
                    
                    file_relationships = self.relationship_extractor.extract(
                        parsed_tree=parse_result.tree,
                        source_code=content,
                        entities=file_entities,
                        source_file=source_file,
                        extraction_result=ext_result
                    )
                    for r in file_relationships:
                        r.metadata["layer"] = "STRUCTURAL"
                    result.relationships.extend(file_relationships)
                    
                    # Store SEEE evidence and compiler outputs
                    if ext_result:
                        from src.infrastructure.persistence.models.evidence_models import SEEEEvidenceModel, CompilerOutputModel
                        
                        seee_ev = SEEEEvidenceModel(
                            id=uuid.uuid4(),
                            file_id=source_file.id.value if hasattr(source_file.id, 'value') else source_file.id,
                            repository_id=repository.id.value if hasattr(repository.id, 'value') else repository.id,
                            file_path=source_file.file_path,
                            commit_hash=commit_hash,
                            symbol_graph=to_json_ready(ext_result.symbol_graph),
                            type_evidence=to_json_ready(ext_result.type_evidence),
                            call_sites=to_json_ready(ext_result.call_sites),
                            dependency_graph={
                                "nodes": to_json_ready(ext_result.dependency_nodes),
                                "edges": to_json_ready(ext_result.dependency_edges)
                            },
                            api_evidence=to_json_ready(ext_result.api_evidence),
                            database_evidence=to_json_ready(ext_result.database_evidence),
                            event_evidence=to_json_ready(ext_result.event_evidence),
                            ai_evidence=to_json_ready(ext_result.ai_evidence),
                            flow_signatures=to_json_ready(ext_result.flow_signatures),
                            structure_signatures=to_json_ready(ext_result.structure_signatures),
                            raw_signals=to_json_ready(ext_result.signals),
                            diagnostics=to_json_ready(ext_result.diagnostics),
                            provenance=to_json_ready(ext_result.provenance)
                        )
                        result.seee_evidences.append(seee_ev)
                        
                        comp_out = CompilerOutputModel(
                            id=uuid.uuid4(),
                            file_id=source_file.id.value if hasattr(source_file.id, 'value') else source_file.id,
                            repository_id=repository.id.value if hasattr(repository.id, 'value') else repository.id,
                            file_path=source_file.file_path,
                            commit_hash=commit_hash,
                            generated_entities=[{
                                "name": e.name,
                                "entity_type": e.entity_type.name if hasattr(e.entity_type, 'name') else str(e.entity_type),
                                "start_line": e.start_line,
                                "end_line": e.end_line
                            } for e in ext_result.entities],
                            generated_relationships=[{
                                "relationship_type": r.relationship_type.name if hasattr(r.relationship_type, 'name') else str(r.relationship_type),
                                "source_name": r.source_name,
                                "target_name": r.target_name
                            } for r in ext_result.relationships],
                            report={},
                            frameworks_detected=[],
                            semantic_hints=[]
                        )
                        result.compiler_outputs.append(comp_out)
                    
                except Exception as ex:
                    logger.error(f"Error processing file {scanned.path}: {ex}")
                    result.errors.append(f"Error in {scanned.path}: {ex}")

            # Run Configuration Intelligence extraction
            try:
                config_entities, config_relationships = self.config_intel_service.scan_repository(local_path, repository.id.value if hasattr(repository.id, 'value') else repository.id)
                # Assign SEMANTIC layer to these entities and relationships
                for e in config_entities:
                    e.metadata["layer"] = "SEMANTIC"
                for r in config_relationships:
                    r.metadata["layer"] = "SEMANTIC"
                result.entities.extend(config_entities)
                result.relationships.extend(config_relationships)
            except Exception as ex:
                logger.error(f"Error running Configuration Intelligence: {ex}")
                result.errors.append(f"Configuration Intelligence Error: {ex}")

            repository.status = AnalysisStatus.EXTRACTING
            return result
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            result.errors.append(str(e))
            return result
