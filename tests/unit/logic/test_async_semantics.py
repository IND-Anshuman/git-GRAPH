"""Unit tests for async semantics extraction and mapping."""

from src.application.semantic.isr import CanonicalEntity
from src.application.semantic.behavior_registry.canonical_registry import CanonicalRegistry
from src.application.semantic.normalization.semantic_normalizer import SemanticNormalizer
from src.application.semantic.type_resolution.type_resolution_engine import TypeResolutionEngine


def test_async_entity_normalization():
    """Verify that asynchronous structures are correctly normalized into canonical ISR entities."""
    registry = CanonicalRegistry()
    type_engine = TypeResolutionEngine()
    normalizer = SemanticNormalizer(registry, type_engine)

    # 1. Coroutine/async function (e.g. C# / Rust)
    raw_coroutine = {
        "name": "FetchDataAsync",
        "qualified_name": "App.Services.DataService.FetchDataAsync",
        "type": "Coroutine",
        "visibility": "public",
        "return_type": "Task<string>",
        "metadata": {"is_async": True}
    }
    entity = normalizer.normalize_entity(raw_coroutine, "csharp")
    assert entity.entity_type == "Coroutine"
    assert entity.name == "FetchDataAsync"
    assert entity.return_type == "Task"
    assert entity.generics == ["string"]
    assert entity.metadata.get("is_async") is True

    # 2. Channel/Queue (e.g. Go / Kotlin)
    raw_channel = {
        "name": "msgChannel",
        "qualified_name": "main.msgChannel",
        "type": "Channel",
        "visibility": "private",
        "return_type": "chan string",
        "metadata": {"capacity": 10}
    }
    entity = normalizer.normalize_entity(raw_channel, "go")
    assert entity.entity_type == "Channel"
    assert entity.name == "msgChannel"
    assert entity.return_type == "chan string"  # Simple unresolved type
    assert entity.metadata.get("capacity") == 10

    # 3. Actor (e.g. Akka/Elixir/Scala)
    raw_actor = {
        "name": "UserSessionActor",
        "qualified_name": "App.Actors.UserSessionActor",
        "type": "Actor",
        "visibility": "public",
        "metadata": {"supervision_strategy": "OneForOne"}
    }
    entity = normalizer.normalize_entity(raw_actor, "scala")
    assert entity.entity_type == "Actor"
    assert entity.name == "UserSessionActor"
    assert entity.metadata.get("supervision_strategy") == "OneForOne"
