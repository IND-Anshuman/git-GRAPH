import uuid
from unittest.mock import MagicMock, patch
import pytest
import datetime

from src.domain.entities.source_file import SourceFile
from src.domain.entities.repository import RepositoryEntity
from src.domain.enums.language import SupportedLanguage
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.value_objects.repository_id import RepositoryId
from src.application.services.ingestion_pipeline import IngestionPipeline
from src.infrastructure.extraction.strategies.wave1_strategy import Wave1ExtractionStrategy

def test_ingestion_pipeline_threads_extraction_result():
    repo_id = RepositoryId.generate()
    
    # 1. Mock the dependencies
    git_adapter = MagicMock()
    git_adapter.clone_repository.return_value = "/tmp/repo"
    
    file_scanner = MagicMock()
    mock_scanned = MagicMock()
    mock_scanned.absolute_path = "src/main.py"
    mock_scanned.path = "src/main.py"
    mock_scanned.language = SupportedLanguage.PYTHON
    mock_scanned.size_bytes = 100
    file_scanner.scan_repository.return_value = [mock_scanned]
    
    parser = MagicMock()
    parse_result = MagicMock()
    parse_result.errors = []
    parse_result.tree = "mock_ast_tree"
    parser.parse_file.return_value = parse_result
    
    entity_extractor = MagicMock()
    mock_result = MagicMock()
    entity_extractor.extract.return_value = ([], mock_result)
    
    relationship_extractor = MagicMock()
    relationship_extractor.extract.return_value = []
    
    identity_service = MagicMock()
    identity_service.compute_content_hash.return_value = "hash1"
    
    pipeline = IngestionPipeline(
        git_adapter=git_adapter,
        file_scanner=file_scanner,
        parser=parser,
        entity_extractor=entity_extractor,
        relationship_extractor=relationship_extractor,
        identity_service=identity_service
    )
    
    now = datetime.datetime.now(datetime.timezone.utc)
    repository = RepositoryEntity(
        id=repo_id,
        url="https://github.com/test/repo",
        name="test-repo",
        default_branch="main",
        local_path=None,
        status=AnalysisStatus.PENDING,
        created_at=now,
        updated_at=now
    )
    
    # Run ingestion
    with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value="code")))))):
        res = pipeline.run(repository=repository, storage_root="/tmp/storage")
    
    # Verify entity_extractor called
    entity_extractor.extract.assert_called_once()
    args, kwargs = entity_extractor.extract.call_args
    assert kwargs["parsed_tree"] == "mock_ast_tree"
    assert kwargs["source_code"] == "code"
    assert kwargs["repository_id"] == repo_id
    
    # Verify relationship_extractor called with the exact extraction_result returned
    relationship_extractor.extract.assert_called_once()
    args_rel, kwargs_rel = relationship_extractor.extract.call_args
    assert kwargs_rel["parsed_tree"] == "mock_ast_tree"
    assert kwargs_rel["source_code"] == "code"
    assert kwargs_rel["extraction_result"] == mock_result

def test_wave1_strategy_uses_passed_extraction_result(monkeypatch):
    # Verify that Wave1ExtractionStrategy does not invoke the underlying engine if extraction_result is passed.
    strategy = Wave1ExtractionStrategy(language_key="python")
    
    # Mock engine dependency or call to extract
    mock_engine = MagicMock()
    
    # Monkeypatch the SemanticEvidenceExtractionEngine class instantiation inside its own module
    import src.infrastructure.extraction.semantic_evidence_engine.semantic_evidence_engine as engine_module
    monkeypatch.setattr(engine_module, "SemanticEvidenceExtractionEngine", lambda: mock_engine)
    
    # Case A: extraction_result is provided
    mock_result = MagicMock()
    mock_result.relationships = ["rel1"]
    
    rels = strategy.extract_relationships(
        tree=None,
        source_code="code",
        entities=[],
        extraction_result=mock_result
    )
    
    # Relationships should be read directly from the result
    assert rels == ["rel1"]
    mock_engine.extract.assert_not_called()
    
    # Case B: extraction_result is None
    # In this case, it must invoke the engine
    mock_engine.extract.return_value = mock_result
    rels_none = strategy.extract_relationships(
        tree=None,
        source_code="code",
        entities=[],
        extraction_result=None
    )
    assert rels_none == ["rel1"]
    mock_engine.extract.assert_called_once_with(None, "code", "")
