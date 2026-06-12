import uuid

from src.domain.entities.source_file import SourceFile
from src.domain.enums.language import SupportedLanguage
from src.domain.services.identity_service import EntityIdentityService
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.infrastructure.extraction.entity_extractor import EntityExtractorService
from src.infrastructure.extraction.relationship_extractor import RelationshipExtractorService
from src.infrastructure.parsing.language_registry import LanguageRegistry


def test_entity_extractor_returns_empty_for_declared_without_strategy():
    service = EntityExtractorService(LanguageRegistry(), EntityIdentityService())
    source_file = SourceFile(
        id=FileId(uuid.uuid4()),
        repository_id=RepositoryId.generate(),
        file_path="index.js",
        language=SupportedLanguage.UNKNOWN,
    )

    assert service.extract(None, "const value = 1;", source_file, source_file.repository_id) == ([], None)


def test_relationship_extractor_returns_empty_for_declared_without_strategy():
    service = RelationshipExtractorService(LanguageRegistry())
    source_file = SourceFile(
        id=FileId(uuid.uuid4()),
        repository_id=RepositoryId.generate(),
        file_path="index.js",
        language=SupportedLanguage.UNKNOWN,
    )

    assert service.extract(None, "const value = 1;", [], source_file) == []
