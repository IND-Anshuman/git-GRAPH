import os
import json
from pathlib import Path
from src.infrastructure.extraction.compiler.semantic_compiler import SemanticCompiler
from src.domain.enums.language import SupportedLanguage

def test_semantic_compiler_python_fixture():
    # Arrange
    fixtures_dir = Path(__file__).parent.parent.parent / "semantic_fixtures" / "python"
    
    source_path = fixtures_dir / "source_code.py"
    entities_path = fixtures_dir / "expected_entities.json"
    rels_path = fixtures_dir / "expected_relationships.json"
    hints_path = fixtures_dir / "expected_hints.json"
    
    with open(source_path, "r", encoding="utf-8") as f:
        source_code = f.read()
    with open(entities_path, "r", encoding="utf-8") as f:
        expected_entities = json.load(f)
    with open(rels_path, "r", encoding="utf-8") as f:
        expected_relationships = json.load(f)
    with open(hints_path, "r", encoding="utf-8") as f:
        expected_hints = json.load(f)
        
    compiler = SemanticCompiler()
    
    # Act
    context = compiler.compile(
        file_path="src/order.py",
        source_code=source_code,
        language="python"
    )
    
    # Assert
    from src.application.dtos.compiler_output import CompilerOutput
    assert isinstance(context, CompilerOutput)

    # 1. Frameworks
    assert "fastapi" in context.frameworks_detected
    assert "langgraph" in context.frameworks_detected
    
    # 2. Entities
    assert len(context.generated_entities) >= 2
    ent_names = [e.name for e in context.generated_entities]
    for exp in expected_entities:
        assert exp["name"] in ent_names
        
    # Check Semantic Roles / Types
    coordinator_ent = next(e for e in context.generated_entities if e.name == "OrderCoordinator")
    service_ent = next(e for e in context.generated_entities if e.name == "OrderService")
    
    assert coordinator_ent.semantic_type is not None
    assert coordinator_ent.semantic_type.name == "Coordinator"
    assert service_ent.semantic_type is not None
    assert service_ent.semantic_type.name == "Service"
    
    # 3. Relationships
    assert len(context.generated_relationships) >= 1
    # Check if there is CALLS relationship
    calls_rel = next(
        (r for r in context.generated_relationships if r.relationship_type == "CALLS"),
        None
    )
    assert calls_rel is not None
    
    # 4. Hints
    assert len(context.semantic_hints) >= 1
    hint_categories = [h.category for h in context.semantic_hints]
    for exp in expected_hints:
        assert exp["category"] in hint_categories
        
    # 5. Report
    assert context.report is not None
    assert context.report.entities_found >= 2
    assert context.report.frameworks_detected == context.frameworks_detected
