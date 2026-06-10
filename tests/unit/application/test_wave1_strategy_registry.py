from src.domain.enums.language import SupportedLanguage
from src.infrastructure.extraction.strategy_registry import ExtractionStrategyRegistry


def test_wave1_languages_have_extraction_strategies():
    registry = ExtractionStrategyRegistry()

    for language in SupportedLanguage:
        if language == SupportedLanguage.UNKNOWN:
            continue
        assert registry.supports(language) is True
