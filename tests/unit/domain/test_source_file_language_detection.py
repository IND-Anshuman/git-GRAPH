from src.domain.entities.source_file import SourceFile
from src.domain.enums.language import SupportedLanguage


def test_detect_language_for_documented_extensions():
    assert SourceFile.detect_language("service.py") == SupportedLanguage.PYTHON
    assert SourceFile.detect_language("index.js") == SupportedLanguage.JAVASCRIPT
    assert SourceFile.detect_language("view.tsx") == SupportedLanguage.TYPESCRIPT
    assert SourceFile.detect_language("main.go") == SupportedLanguage.GO
    assert SourceFile.detect_language("App.java") == SupportedLanguage.JAVA
    assert SourceFile.detect_language("Program.cs") == SupportedLanguage.CSHARP
    assert SourceFile.detect_language("lib.rs") == SupportedLanguage.RUST
    assert SourceFile.detect_language("service.kt") == SupportedLanguage.KOTLIN
    assert SourceFile.detect_language("Feature.swift") == SupportedLanguage.SWIFT
    assert SourceFile.detect_language("index.php") == SupportedLanguage.PHP
    assert SourceFile.detect_language("build.scala") == SupportedLanguage.SCALA
    assert SourceFile.detect_language("app.rb") == SupportedLanguage.RUBY
    assert SourceFile.detect_language("worker.exs") == SupportedLanguage.ELIXIR
    assert SourceFile.detect_language("page.html") == SupportedLanguage.HTML
    assert SourceFile.detect_language("styles.css") == SupportedLanguage.CSS


def test_detect_language_is_case_insensitive():
    assert SourceFile.detect_language("MODULE.PY") == SupportedLanguage.PYTHON
    assert SourceFile.detect_language("COMPONENT.TSX") == SupportedLanguage.TYPESCRIPT
