"""Integration tests for Repository Semantic Resolution, Governance, and new database tables."""

import uuid
from datetime import datetime, timezone
import pytest

from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.application.semantic.resolution import (
    GlobalSemanticGraph,
    CanonicalSymbol,
    SymbolResolutionEngine,
    AliasPropagationEngine,
    CrossFileCallResolver,
    ExternalDependencyResolver,
)
from src.infrastructure.persistence.models.resolution_models import (
    SymbolGraphModel,
    SymbolReferenceModel,
    VariableFlowModel,
    CrossFileResolutionModel,
    ExternalDependencyModel,
    AIEvidenceModel,
    RepositoryArchitectureGraphModel,
    ArchitectureRelationshipModel,
    RepositoryStructureGraphModel,
    CompilerOutputVersionModel,
    ReasoningArtifactModel,
    KnowledgeDriftModel,
    ExternalKnowledgeReferenceModel,
)
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.compiler import SemanticCompiler

class DummyEngine:
    def __init__(self, session):
        self.session_factory = lambda: session

def test_semantic_resolution_and_variable_propagation():
    """Test global graph indexing, target resolution, and variable propagation flow."""
    global_graph = GlobalSemanticGraph()
    symbol_engine = SymbolResolutionEngine(global_graph)
    alias_engine = AliasPropagationEngine(global_graph)
    ext_resolver = ExternalDependencyResolver(global_graph)
    cross_resolver = CrossFileCallResolver(global_graph)

    # 1. Index file 1: utils/auth.py defining verify_password
    auth_code = """
class PasswordHasher:
    def verify_password(self, pwd):
        pass
"""
    registry = LanguageRegistry()
    adapter = registry.get_adapter(SupportedLanguage.PYTHON)
    parser = adapter.get_parser()
    auth_tree = parser.parse(bytes(auth_code, "utf8"))

    symbol_engine.index_file("utils/auth.py", auth_code, auth_tree, "python")

    # 2. Index file 2: services/user.py using verify_password & redis
    user_code = """
import redis as r
from utils.auth import PasswordHasher

def create_user():
    hasher = PasswordHasher()
    a = "pass123"
    b = a
    hasher.verify_password(b)
    r.get("token")
"""
    user_tree = parser.parse(bytes(user_code, "utf8"))

    symbol_engine.index_file("services/user.py", user_code, user_tree, "python")
    flows = alias_engine.trace_variable_flows("services/user.py", user_code, user_tree)
    ext_resolver.resolve_external_imports("services/user.py", global_graph.imports.get("services/user.py", []))

    # Assertions
    # Check symbols registered
    assert "utils.auth.PasswordHasher" in global_graph.symbols
    assert "utils.auth.PasswordHasher.verify_password" in global_graph.symbols

    # Check imports
    imports = global_graph.imports.get("services/user.py", [])
    assert any(imp["module_name"] == "redis" and imp["alias"] == "r" for imp in imports)
    assert any(imp["module_name"] == "utils.auth" and imp["symbol_name"] == "PasswordHasher" for imp in imports)

    # Check external dependency resolver stub node
    assert "Redis" in global_graph.external_dependencies
    assert global_graph.external_dependencies["Redis"]["type"] == "EXTERNAL_SERVICE"

    # Check alias propagation flow (lineage)
    assert any(f["source"] == "a" and f["target"] == "b" for f in flows)
    assert global_graph.aliases["services/user.py"]["b"] == "a"

    # Check cross-file calls resolution
    # hasher.verify_password -> PasswordHasher.verify_password -> utils.auth.PasswordHasher.verify_password
    resolved_hasher = cross_resolver.resolve_call("services/user.py", "hasher.verify_password")
    assert resolved_hasher == "utils.auth.PasswordHasher.verify_password"

    # r.get -> redis.get
    resolved_redis = cross_resolver.resolve_call("services/user.py", "r.get")
    assert "redis" in resolved_redis


def test_compiler_resolution_integration():
    """Test integrating global_semantic_graph into master SemanticCompiler."""
    compiler = SemanticCompiler()
    global_graph = GlobalSemanticGraph()
    symbol_engine = SymbolResolutionEngine(global_graph)
    alias_engine = AliasPropagationEngine(global_graph)
    ext_resolver = ExternalDependencyResolver(global_graph)
    cross_resolver = CrossFileCallResolver(global_graph)

    project_metadata = {
        "global_semantic_graph": global_graph,
        "symbol_resolution_engine": symbol_engine,
        "alias_propagation_engine": alias_engine,
        "external_dependency_resolver": ext_resolver,
        "cross_file_call_resolver": cross_resolver,
    }

    auth_code = """
class PasswordHasher:
    def verify_password(self, pwd):
        pass
"""
    # Pre-index utils/auth.py
    registry = LanguageRegistry()
    adapter = registry.get_adapter(SupportedLanguage.PYTHON)
    auth_tree = adapter.get_parser().parse(bytes(auth_code, "utf8"))
    symbol_engine.index_file("utils/auth.py", auth_code, auth_tree, "python")

    user_code = """
from utils.auth import PasswordHasher

def create_user():
    hasher = PasswordHasher()
    hasher.verify_password("123")
"""

    # Compile services/user.py
    output = compiler.compile(
        file_path="services/user.py",
        source_code=user_code,
        language="python",
        project_metadata=project_metadata
    )

    # Check if cross-file CALLS resolves correctly
    calls = [r for r in output.generated_relationships if r.relationship_type == "CALLS"]
    assert len(calls) > 0
    verify_call = next((c for c in calls if "verify_password" in c.to_entity_id), None)
    assert verify_call is not None
    assert verify_call.to_entity_id == "utils.auth.PasswordHasher.verify_password"


def test_persistence_expansion_flow(db_session):
    """Test persisting and retrieving all 13 new SQLAlchemy models via unit of work."""
    uow = SQLAlchemyUnitOfWork(DummyEngine(db_session))
    repo_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    # Setup mock repository record (needed for FK constraints)
    from src.infrastructure.persistence.models import RepositoryModel
    repo_model = RepositoryModel(
        id=repo_id,
        name="test-resolution-repo",
        url="https://github.com/test/resolution",
        default_branch="main",
        status="COMPLETED"
    )
    db_session.add(repo_model)
    db_session.commit()

    with uow:
        # 1. SymbolGraphModel
        sym_node = SymbolGraphModel(
            id=uuid.uuid4(),
            repository_id=repo_id,
            symbol_id="sym_verify_password",
            canonical_name="utils.auth.verify_password",
            scope_id="PasswordHasher",
            entity_type="METHOD",
            file_path="utils/auth.py",
            created_at=now,
            metadata={}
        )
        uow.symbol_graph.save(sym_node)

        # 2. SymbolReferenceModel
        sym_ref = SymbolReferenceModel(
            id=uuid.uuid4(),
            repository_id=repo_id,
            source_symbol_id="sym_create_user",
            target_symbol_id="sym_verify_password",
            reference_type="CALLS",
            created_at=now
        )
        uow.symbol_references.save(sym_ref)

        # 3. VariableFlowModel
        var_flow = VariableFlowModel(
            id=uuid.uuid4(),
            repository_id=repo_id,
            file_path="services/user.py",
            source_variable="a",
            target_variable="b",
            flow_type="variable_assignment",
            created_at=now
        )
        uow.variable_flows.save(var_flow)

        # 4. CrossFileResolutionModel
        cross_res = CrossFileResolutionModel(
            id=uuid.uuid4(),
            repository_id=repo_id,
            source_file="services/user.py",
            source_entity="create_user",
            target_file="utils/auth.py",
            target_entity="PasswordHasher.verify_password",
            relationship_type="CALLS",
            created_at=now
        )
        uow.cross_file_resolutions.save(cross_res)

        # 5. ExternalDependencyModel
        ext_dep = ExternalDependencyModel(
            id=uuid.uuid4(),
            repository_id=repo_id,
            dependency_name="OpenAI",
            dependency_type="EXTERNAL_MODEL",
            created_at=now,
            metadata={}
        )
        uow.external_dependencies.save(ext_dep)

        # 6. AIEvidenceModel
        ai_ev = AIEvidenceModel(
            id=uuid.uuid4(),
            repository_id=repo_id,
            file_path="agents/planner.py",
            class_name="AgentPlanner",
            method_name="plan",
            pattern_matched="ai_agent_plan",
            evidence_type="AST_CALL",
            confidence=0.95,
            created_at=now,
            metadata={}
        )
        uow.ai_evidences.save(ai_ev)

        # 7. RepositoryArchitectureGraphModel
        arch_node = RepositoryArchitectureGraphModel(
            id=uuid.uuid4(),
            repository_id=repo_id,
            node_id="domain.payments",
            node_name="Payments",
            node_type="DOMAIN",
            owner_team="Team A",
            created_at=now,
            metadata={}
        )
        uow.architecture_graphs.save(arch_node)

        # 8. ArchitectureRelationshipModel
        arch_rel = ArchitectureRelationshipModel(
            id=uuid.uuid4(),
            repository_id=repo_id,
            source_node_id="domain.payments",
            target_node_id="bounded_context.checkout",
            relationship_type="DEPENDS_ON",
            created_at=now
        )
        uow.architecture_relationships.save(arch_rel)

        # 9. RepositoryStructureGraphModel
        struct_node = RepositoryStructureGraphModel(
            id=uuid.uuid4(),
            repository_id=repo_id,
            source_file_path="services/user.py",
            target_file_path="utils/auth.py",
            relationship_type="IMPORTS",
            created_at=now,
            metadata={}
        )
        uow.structure_graphs.save(struct_node)

        # 10. CompilerOutputVersionModel
        comp_ver = CompilerOutputVersionModel(
            id=uuid.uuid4(),
            repository_id=repo_id,
            file_path="services/user.py",
            commit_hash="hash123",
            compiler_version="V2.0.0",
            rules_hash="rules_sha_12345",
            generated_at=now
        )
        uow.compiler_output_versions.save(comp_ver)

        # 11. ReasoningArtifactModel
        reason_art = ReasoningArtifactModel(
            id=uuid.uuid4(),
            repository_id=repo_id,
            artifact_type="architecture_classification",
            content={"architecture": "CQRS"},
            confidence=0.92,
            validation_status="PROPOSED",
            evidence_refs=["services/user.py"],
            supporting_entities=[],
            supporting_relationships=[],
            supporting_behaviors=[],
            created_at=now,
            updated_at=now
        )
        uow.reasoning_artifacts.save(reason_art)

        # 12. KnowledgeDriftModel
        k_drift = KnowledgeDriftModel(
            id=uuid.uuid4(),
            repository_id=repo_id,
            drift_type="ARCHITECTURE_DRIFT",
            element_id="CQRS",
            from_value="CQRS",
            to_value="Layered Architecture",
            drift_score=0.85,
            detected_at=now,
            metadata={}
        )
        uow.knowledge_drifts.save(k_drift)

        # 13. ExternalKnowledgeReferenceModel
        ext_ref = ExternalKnowledgeReferenceModel(
            id=uuid.uuid4(),
            source_repository_id=repo_id,
            target_repository_name="payment-service-repo",
            dependency_type="API_CONSUMPTION",
            api_endpoint="/v1/payments",
            created_at=now,
            metadata={}
        )
        uow.external_knowledge_references.save(ext_ref)

        uow.commit()

    # Verify retrieval
    with uow:
        assert len(uow.symbol_graph.list_by_repository(repo_id)) == 1
        assert len(uow.symbol_references.list_by_repository(repo_id)) == 1
        assert len(uow.variable_flows.list_by_repository(repo_id)) == 1
        assert len(uow.cross_file_resolutions.list_by_repository(repo_id)) == 1
        assert len(uow.external_dependencies.list_by_repository(repo_id)) == 1
        assert len(uow.ai_evidences.list_by_repository(repo_id)) == 1
        assert len(uow.architecture_graphs.list_by_repository(repo_id)) == 1
        assert len(uow.architecture_relationships.list_by_repository(repo_id)) == 1
        assert len(uow.structure_graphs.list_by_repository(repo_id)) == 1
        assert len(uow.compiler_output_versions.list_by_repository(repo_id)) == 1
        assert len(uow.reasoning_artifacts.list_by_repository(repo_id)) == 1
        assert len(uow.knowledge_drifts.list_by_repository(repo_id)) == 1
        assert len(uow.external_knowledge_references.list_by_repository(repo_id)) == 1
