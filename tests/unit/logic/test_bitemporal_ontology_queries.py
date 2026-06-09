"""Unit tests for bitemporal ontology queries, snapshots, and diffs using SemanticEvolutionEngine."""

import pytest
import uuid
from datetime import datetime, timezone
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
from src.domain.enums.mutation_type import MutationType
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.relationship import Relationship
from src.domain.entities.repository import RepositoryEntity
from src.domain.entities.source_file import SourceFile
from src.domain.entities.commit import Commit
from src.domain.entities.entity_version import EntityVersion
from src.domain.entities.logic_signature import LogicSignature
from src.domain.entities.logic_version import LogicVersion
from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.value_objects.logic_fingerprint import LogicFingerprint
from src.domain.enums.analysis_status import AnalysisStatus
from src.application.services.historical_reconstruction import HistoricalReconstructionService
from src.application.semantic.evolution.semantic_evolution_engine import SemanticEvolutionEngine


class DummyDatabaseEngine:
    def __init__(self, session_factory):
        self.session_factory = session_factory


@pytest.fixture
def uow(db_engine):
    session_factory = sessionmaker(bind=db_engine)
    db_mock = DummyDatabaseEngine(session_factory)
    return SQLAlchemyUnitOfWork(db_mock)


def test_bitemporal_evolution_queries(uow):
    """Seed mutating code, behaviors, and concepts, verifying graph_at_commit and graph_diff return correct diffs."""
    reconstructor = HistoricalReconstructionService()
    engine = SemanticEvolutionEngine(uow, reconstructor)
    
    repo_id = RepositoryId.generate()
    file_id = FileId.generate()
    now = datetime.now(timezone.utc)
    location = CodeLocation(file_path="src/main.py", start_line=1, end_line=10, start_column=0, end_column=0)
    struct_hash = StructuralFingerprint(value="sf-hash")

    commit_hash_1 = "1111111111111111111111111111111111111111"
    commit_hash_2 = "2222222222222222222222222222222222222222"

    with uow:
        # Seed Repo
        repo = RepositoryEntity(
            id=repo_id,
            url="https://github.com/test/bitemporal",
            name="bitemporal",
            default_branch="main",
            local_path="src/",
            status=AnalysisStatus.COMPLETED,
            created_at=now,
            updated_at=now
        )
        uow.repositories.save(repo)

        # Seed SourceFile
        source_file = SourceFile(
            id=file_id,
            repository_id=repo_id,
            file_path="src/main.py",
            language=SupportedLanguage.PYTHON
        )
        uow.source_files.save(source_file)

        # Seed Commits
        c1 = Commit(commit_hash_1, repo_id, "Author", "email", now, "C1 message", [])
        c2 = Commit(commit_hash_2, repo_id, "Author", "email", now, "C2 message", [commit_hash_1])
        uow.commits.save(c1)
        uow.commits.save(c2)

        # Seed Entities
        seid1 = SEID.generate()
        seid2 = SEID.generate()

        entity1 = CodeEntity(
            seid=seid1,
            entity_type=EntityType.FUNCTION,
            name="func1",
            qualified_name="func1",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=location,
            structural_fingerprint=struct_hash
        )
        entity2 = CodeEntity(
            seid=seid2,
            entity_type=EntityType.FUNCTION,
            name="func2",
            qualified_name="func2",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=location,
            structural_fingerprint=struct_hash
        )
        uow.code_entities.save(entity1)
        uow.code_entities.save(entity2)

        # Seed EntityVersions (Entity1 created at Commit1, Entity2 created at Commit2)
        ev1 = EntityVersion(
            id=uuid.uuid4(),
            seid=seid1,
            commit_hash=commit_hash_1,
            version_ordinal=1,
            mutation_type=MutationType.CREATED,
            canonical_name="func1",
            file_path="src/main.py",
            start_line=1,
            end_line=10,
            content_hash="hash-1",
            structural_fingerprint="sf-1"
        )
        ev2 = EntityVersion(
            id=uuid.uuid4(),
            seid=seid2,
            commit_hash=commit_hash_2,
            version_ordinal=1,
            mutation_type=MutationType.CREATED,
            canonical_name="func2",
            file_path="src/main.py",
            start_line=1,
            end_line=10,
            content_hash="hash-2",
            structural_fingerprint="sf-2"
        )
        uow.entity_versions.save(ev1)
        uow.entity_versions.save(ev2)

        # Seed LogicSignature
        sig1 = LogicSignature(
            id=uuid.uuid4(),
            repository_id=repo_id,
            canonical_name="logic_sig_1",
            language=SupportedLanguage.PYTHON,
            ontology_node_id="security.authentication",
            description="Auth logic",
            created_at=now
        )
        uow.logic_signatures.save(sig1)

        # Seed LogicVersions (Version 1 at Commit1, Version 2 at Commit2)
        lv1 = LogicVersion(
            id=uuid.uuid4(),
            logic_signature_id=sig1.id,
            code_entity_seid=seid1,
            commit_hash=commit_hash_1,
            version_ordinal=1,
            fingerprint=LogicFingerprint("a", "b", "c", "abc"),
            overall_confidence=0.85,
            is_primary=True,
            created_at=now
        )
        lv2 = LogicVersion(
            id=uuid.uuid4(),
            logic_signature_id=sig1.id,
            code_entity_seid=seid1,
            commit_hash=commit_hash_2,
            version_ordinal=2,
            fingerprint=LogicFingerprint("d", "e", "f", "def"),
            overall_confidence=0.90,
            is_primary=True,
            created_at=now
        )
        uow.logic_versions.save(lv1)
        uow.logic_versions.save(lv2)

        # Seed ConceptNode & Versions (Active at Commit2, but not at Commit1)
        concept_id = uuid.uuid4()
        c_node = ConceptNode(
            id=concept_id,
            repository_id=repo_id,
            ontology_node_id="security.authentication",
            name="Authentication",
            description="Auth",
            is_system_defined=False
        )
        uow.concept_nodes.save(c_node)

        cv2 = ConceptVersion(
            id=uuid.uuid4(),
            concept_id=concept_id,
            commit_hash=commit_hash_2,
            version_number=1,
            confidence=0.95,
            is_active=True,
            created_at=now
        )
        uow.concept_versions.save(cv2)

        uow.commit()

    # 3. Retrieve snap at Commit 1
    snap1 = engine.graph_at_commit(repo_id, commit_hash_1)
    assert len(snap1["entities"]) == 1
    assert str(snap1["entities"][0].seid.value) == str(seid1.value)
    assert len(snap1["behaviors"]) == 1
    assert snap1["behaviors"][0].commit_hash == commit_hash_1
    assert len(snap1["concepts"]) == 0

    # 4. Retrieve snap at Commit 2
    snap2 = engine.graph_at_commit(repo_id, commit_hash_2)
    assert len(snap2["entities"]) == 2
    assert len(snap2["behaviors"]) == 1
    assert snap2["behaviors"][0].commit_hash == commit_hash_2
    assert len(snap2["concepts"]) == 1
    assert snap2["concepts"][0].id == concept_id

    # 5. Compute graph diff between Commit 1 and Commit 2
    diff = engine.graph_diff(repo_id, commit_hash_1, commit_hash_2)
    
    assert len(diff["added_entities"]) == 1
    assert str(diff["added_entities"][0].seid.value) == str(seid2.value)
    assert len(diff["removed_entities"]) == 0

    assert len(diff["added_concepts"]) == 1
    assert diff["added_concepts"][0].id == concept_id
