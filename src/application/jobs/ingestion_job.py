"""Job for executing core repository ingestion (SEEE, parsing, config intelligence)."""

import uuid
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.services.ingestion_pipeline import IngestionPipeline
from src.domain.entities import RepositoryEntity

class IngestionJob:
    """Synchronous job executing SEEE, parsing, persistence, and Configuration Intelligence."""
    
    def __init__(self, pipeline: IngestionPipeline, uow_factory):
        self.pipeline = pipeline
        self.uow_factory = uow_factory
        
    def run(self, repository: RepositoryEntity, storage_root: str) -> dict:
        result = self.pipeline.run(repository, storage_root)
        
        with self.uow_factory() as uow:
            repo_in_db = uow.repositories.get_by_id(repository.id)
            if repo_in_db:
                if result.files:
                    uow.source_files.save_batch(result.files)
                if result.entities:
                    uow.code_entities.save_batch(result.entities)
                if result.relationships:
                    uow.relationships.save_batch(result.relationships)
                    
                if hasattr(result, 'seee_evidences') and result.seee_evidences:
                    uow._session.add_all(result.seee_evidences)
                if hasattr(result, 'compiler_outputs') and result.compiler_outputs:
                    uow._session.add_all(result.compiler_outputs)
                    
                repo_in_db.local_path = repository.local_path
                repo_in_db.status = repository.status
                uow.repositories.save(repo_in_db)
                uow.commit()
                
        return {
            "files_scanned": len(result.files),
            "entities_extracted": len(result.entities),
            "relationships_extracted": len(result.relationships),
            "errors": result.errors
        }
