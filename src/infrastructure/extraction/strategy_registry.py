"""Registry for mapping languages to extraction strategies."""

from typing import Dict, Optional

from src.domain.enums.language import SupportedLanguage
from src.infrastructure.extraction.strategies.base import IExtractionStrategy
from src.infrastructure.extraction.strategies.python_strategy import PythonExtractionStrategy
from src.infrastructure.extraction.strategies.wave1_strategy import (
    Wave1ExtractionStrategy,
)


class ExtractionStrategyRegistry:
    """Keeps structural extraction wiring separate from parser registration."""

    def __init__(self) -> None:
        self._strategies: Dict[SupportedLanguage, IExtractionStrategy] = {}
        self._register_default_strategies()

    def _register_default_strategies(self) -> None:
        self.register(SupportedLanguage.PYTHON, PythonExtractionStrategy())
        self.register(
            SupportedLanguage.JAVASCRIPT,
            Wave1ExtractionStrategy("javascript"),
        )
        self.register(
            SupportedLanguage.TYPESCRIPT,
            Wave1ExtractionStrategy("typescript"),
        )
        self.register(
            SupportedLanguage.GO,
            Wave1ExtractionStrategy("go"),
        )
        self.register(
            SupportedLanguage.JAVA,
            Wave1ExtractionStrategy("java"),
        )
        self.register(
            SupportedLanguage.CSHARP,
            Wave1ExtractionStrategy("csharp"),
        )
        self.register(
            SupportedLanguage.RUST,
            Wave1ExtractionStrategy("rust"),
        )
        self.register(
            SupportedLanguage.KOTLIN,
            Wave1ExtractionStrategy("kotlin"),
        )
        self.register(
            SupportedLanguage.SWIFT,
            Wave1ExtractionStrategy("swift"),
        )
        self.register(
            SupportedLanguage.PHP,
            Wave1ExtractionStrategy("php"),
        )
        self.register(
            SupportedLanguage.SCALA,
            Wave1ExtractionStrategy("scala"),
        )
        self.register(
            SupportedLanguage.RUBY,
            Wave1ExtractionStrategy("ruby"),
        )
        self.register(
            SupportedLanguage.ELIXIR,
            Wave1ExtractionStrategy("elixir"),
        )
        self.register(
            SupportedLanguage.HTML,
            Wave1ExtractionStrategy("html"),
        )
        self.register(
            SupportedLanguage.CSS,
            Wave1ExtractionStrategy("css"),
        )

    def register(
        self, language: SupportedLanguage, strategy: IExtractionStrategy
    ) -> None:
        self._strategies[language] = strategy

    def get(self, language: SupportedLanguage) -> Optional[IExtractionStrategy]:
        return self._strategies.get(language)

    def supports(self, language: SupportedLanguage) -> bool:
        return language in self._strategies
