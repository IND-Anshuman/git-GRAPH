from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry


def test_language_registry_declares_all_documented_languages():
    registry = LanguageRegistry()

    declared = {
        capability.language for capability in registry.list_capabilities()
    }

    expected = {
        language for language in SupportedLanguage if language != SupportedLanguage.UNKNOWN
    }
    assert declared == expected


def test_language_registry_reports_python_as_fully_supported():
    registry = LanguageRegistry()

    capability = registry.get_capability(SupportedLanguage.PYTHON)

    assert capability.parser_available is True
    assert capability.entity_extraction_supported is True
    assert capability.relationship_extraction_supported is True


def test_language_registry_reports_declared_but_unavailable_grammars():
    registry = LanguageRegistry()

    capability = registry.get_capability(SupportedLanguage.JAVASCRIPT)

    assert capability.language == SupportedLanguage.JAVASCRIPT
    assert capability.missing_dependency is None or isinstance(
        capability.missing_dependency, str
    )
