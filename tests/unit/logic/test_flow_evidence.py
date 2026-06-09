"""Unit tests for flow discovery, evidence generation, and structural fingerprinting."""

import pytest
import uuid
from datetime import datetime
from sqlalchemy.orm import sessionmaker

from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.code_location import CodeLocation
from src.domain.value_objects.fingerprint import StructuralFingerprint
from src.domain.enums.entity_type import EntityType
from src.domain.enums.relationship_type import RelationshipType
from src.domain.enums.language import SupportedLanguage
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.relationship import Relationship
from src.domain.entities.repository import RepositoryEntity
from src.domain.entities.source_file import SourceFile
from src.domain.enums.analysis_status import AnalysisStatus
from src.application.semantic.discovery.flow_discovery_engine import FlowDiscoveryEngine
from src.domain.value_objects.flow_fingerprint import FlowFingerprint


class DummyDatabaseEngine:
    def __init__(self, session_factory):
        self.session_factory = session_factory


@pytest.fixture
def uow(db_engine):
    session_factory = sessionmaker(bind=db_engine)
    db_mock = DummyDatabaseEngine(session_factory)
    return SQLAlchemyUnitOfWork(db_mock)


def test_flow_discovery_and_fingerprinting(uow):
    """Verify flow tracing across AI component structures and standard messaging sequences."""
    engine = FlowDiscoveryEngine(uow)
    repo_id = RepositoryId.generate()
    file_id = FileId.generate()
    
    # Simple coordinates
    location = CodeLocation(file_path="src/ai_agent.py", start_line=1, end_line=30, start_column=0, end_column=0)
    struct_hash = StructuralFingerprint(value="struct-fingerprint")

    # 1. Seed Repository and SourceFile
    with uow:
        repo = RepositoryEntity(
            id=repo_id,
            url="https://github.com/test/flow-repo",
            name="flow-repo",
            default_branch="main",
            local_path="src/",
            status=AnalysisStatus.COMPLETED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        uow.repositories.save(repo)

        source_file = SourceFile(
            id=file_id,
            repository_id=repo_id,
            file_path="src/ai_agent.py",
            language=SupportedLanguage.PYTHON
        )
        uow.source_files.save(source_file)

        # Seed AI pipeline entities: Agent -> Planner -> Router -> Model
        agent_id = SEID.generate()
        planner_id = SEID.generate()
        router_id = SEID.generate()
        model_id = SEID.generate()

        agent_entity = CodeEntity(
            seid=agent_id,
            entity_type=EntityType.CLASS,
            name="OrchestratorAgent",
            qualified_name="OrchestratorAgent",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=location,
            structural_fingerprint=struct_hash,
            metadata={"entity_type": "Agent"}
        )
        planner_entity = CodeEntity(
            seid=planner_id,
            entity_type=EntityType.CLASS,
            name="CoTPlanner",
            qualified_name="CoTPlanner",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=location,
            structural_fingerprint=struct_hash,
            metadata={"entity_type": "Planner"}
        )
        router_entity = CodeEntity(
            seid=router_id,
            entity_type=EntityType.CLASS,
            name="LLMRouter",
            qualified_name="LLMRouter",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=location,
            structural_fingerprint=struct_hash,
            metadata={"entity_type": "Router"}
        )
        model_entity = CodeEntity(
            seid=model_id,
            entity_type=EntityType.CLASS,
            name="GPT4Model",
            qualified_name="GPT4Model",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=location,
            structural_fingerprint=struct_hash,
            metadata={"entity_type": "Model"}
        )

        uow.code_entities.save(agent_entity)
        uow.code_entities.save(planner_entity)
        uow.code_entities.save(router_entity)
        uow.code_entities.save(model_entity)

        # Seed relationships
        r1 = Relationship(
            id=uuid.uuid4(),
            repository_id=repo_id,
            relationship_type=RelationshipType.CALLS,
            source_seid=agent_id,
            target_seid=planner_id,
            confidence=1.0,
            metadata={}
        )
        r2 = Relationship(
            id=uuid.uuid4(),
            repository_id=repo_id,
            relationship_type=RelationshipType.CALLS,
            source_seid=planner_id,
            target_seid=router_id,
            confidence=1.0,
            metadata={}
        )
        r3 = Relationship(
            id=uuid.uuid4(),
            repository_id=repo_id,
            relationship_type=RelationshipType.CALLS_MODEL,
            source_seid=router_id,
            target_seid=model_id,
            confidence=1.0,
            metadata={}
        )

        uow.relationships.save(r1)
        uow.relationships.save(r2)
        uow.relationships.save(r3)

        uow.commit()

    # 2. Discover flows
    flows = engine.discover_flows(repo_id)

    # 3. Assertions
    # We expect the full path: agent -> planner -> router -> model (length 4)
    # Plus intermediate subsets traversed by DFS
    assert len(flows) >= 1
    
    # Let's find the longest traced path
    longest_flow = max(flows, key=lambda f: len(f.intermediate_entities))
    assert longest_flow.flow_type == "AI Flow"
    assert longest_flow.source_entity_id == str(agent_id.value)
    assert longest_flow.target_entity_id == str(model_id.value)
    assert longest_flow.intermediate_entities == [str(planner_id.value), str(router_id.value)]

    # Validate fingerprint properties
    fingerprint_dict = longest_flow.metadata.get("fingerprint", {})
    assert fingerprint_dict is not None
    assert fingerprint_dict.get("hop_count") == 3
    assert "Agent" in fingerprint_dict.get("node_sequence", [])
    assert "Model" in fingerprint_dict.get("node_sequence", [])

    # Validate similarity helper
    fp1 = FlowFingerprint.from_dict(fingerprint_dict)
    # Identical fingerprint similarity
    assert fp1.calculate_similarity(fp1) == 1.0
