"""Integration tests for historical reconstruction service."""

import datetime
import uuid
from src.domain.entities.commit import Commit
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.entity_version import EntityVersion
from src.domain.enums.mutation_type import MutationType
from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.domain.value_objects.fingerprint import StructuralFingerprint
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.application.services.historical_reconstruction import HistoricalReconstructionService

class DummyEngine:
    def __init__(self, session):
        self.session_factory = lambda: session

def test_historical_reconstruction_lifecycle(db_session):
    repo_id = RepositoryId.generate()
    seid = SEID.generate()
    file_id = FileId(uuid.uuid4())
    
    uow = SQLAlchemyUnitOfWork(DummyEngine(db_session))
    
    with uow:
        # Create commit records (hash1 -> hash2 -> hash3)
        now = datetime.datetime.now(datetime.timezone.utc)
        commit1 = Commit("hash1", repo_id, "Auth", "email", now, "C1", [])
        commit2 = Commit("hash2", repo_id, "Auth", "email", now, "C2", ["hash1"])
        commit3 = Commit("hash3", repo_id, "Auth", "email", now, "C3", ["hash2"])
        
        uow.commits.save(commit1)
        uow.commits.save(commit2)
        uow.commits.save(commit3)
        
        # Create CodeEntity template
        entity = CodeEntity(
            seid=seid,
            entity_type=EntityType.FUNCTION,
            name="func",
            qualified_name="func",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=CodeLocation("src/file.py", 1, 5, 0, 0),
            metadata={"version_count": 3}
        )
        uow.code_entities.save(entity)

        # Version 1: CREATED
        ev1 = EntityVersion(
            id=uuid.uuid4(),
            seid=seid,
            commit_hash="hash1",
            version_ordinal=1,
            mutation_type=MutationType.CREATED,
            canonical_name="func",
            file_path="src/file.py",
            start_line=1,
            end_line=5,
            content_hash="v1",
            structural_fingerprint="fp1"
        )
        uow.entity_versions.save(ev1)

        # Version 2: MODIFIED (name updated to func_v2)
        ev2 = EntityVersion(
            id=uuid.uuid4(),
            seid=seid,
            commit_hash="hash2",
            version_ordinal=2,
            mutation_type=MutationType.MODIFIED,
            canonical_name="func_v2",
            file_path="src/file.py",
            start_line=1,
            end_line=10,
            content_hash="v2",
            structural_fingerprint="fp2"
        )
        uow.entity_versions.save(ev2)

        # Version 3: DELETED
        ev3 = EntityVersion(
            id=uuid.uuid4(),
            seid=seid,
            commit_hash="hash3",
            version_ordinal=3,
            mutation_type=MutationType.DELETED,
            canonical_name="func_v2",
            file_path="src/file.py",
            start_line=1,
            end_line=10,
            content_hash="v2",
            structural_fingerprint="fp2"
        )
        uow.entity_versions.save(ev3)
        
        uow.commit()

    # Reconstruct state at hash1
    reconstruction_service = HistoricalReconstructionService()
    
    with uow:
        entities, rels = reconstruction_service.reconstruct_graph_at_commit(uow, repo_id, "hash1")
        assert len(entities) == 1
        assert entities[0].name == "func"
        assert entities[0].location.end_line == 5

        # Reconstruct state at hash2
        entities2, rels2 = reconstruction_service.reconstruct_graph_at_commit(uow, repo_id, "hash2")
        assert len(entities2) == 1
        assert entities2[0].name == "func_v2"
        assert entities2[0].location.end_line == 10

        # Reconstruct state at hash3 (should be empty because it was deleted)
        entities3, rels3 = reconstruction_service.reconstruct_graph_at_commit(uow, repo_id, "hash3")
        assert len(entities3) == 0
