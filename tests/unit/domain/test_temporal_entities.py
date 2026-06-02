"""Unit tests for Phase 2 temporal domain entities."""

from datetime import datetime, timezone
import uuid
from src.domain.entities.commit import Commit
from src.domain.entities.entity_version import EntityVersion
from src.domain.entities.relationship_version import RelationshipVersion
from src.domain.entities.change_event import ChangeEvent
from src.domain.entities.repository_snapshot import RepositorySnapshot
from src.domain.enums.mutation_type import MutationType
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.entity_id import SEID

def test_commit_invariants():
    repo_id = RepositoryId.generate()
    now = datetime.now(timezone.utc)
    
    # Root commit
    root = Commit("hash1", repo_id, "Author", "email", now, "Initial commit", [])
    assert root.is_root
    assert not root.is_merge

    # Standard commit
    commit = Commit("hash2", repo_id, "Author", "email", now, "msg", ["hash1"])
    assert not commit.is_root
    assert not commit.is_merge

    # Merge commit
    merge = Commit("hash3", repo_id, "Author", "email", now, "merge msg", ["hash1", "hash2"])
    assert not merge.is_root
    assert merge.is_merge

def test_entity_version_invariants():
    seid = SEID.generate()
    version_id = uuid.uuid4()
    
    version = EntityVersion(
        id=version_id,
        seid=seid,
        commit_hash="hash1",
        version_ordinal=1,
        mutation_type=MutationType.CREATED,
        canonical_name="module.func",
        file_path="src/module.py",
        start_line=1,
        end_line=10,
        content_hash="contenthash",
        structural_fingerprint="structhash"
    )
    
    assert version.id == version_id
    assert version.seid == seid
    assert version.mutation_type == MutationType.CREATED
    assert version.version_ordinal == 1

def test_relationship_version_invariants():
    rel_id = uuid.uuid4()
    version_id = uuid.uuid4()
    
    version = RelationshipVersion(
        id=version_id,
        relationship_id=rel_id,
        commit_hash="hash1",
        mutation_type=MutationType.CREATED,
        version_ordinal=1
    )
    
    assert version.id == version_id
    assert version.relationship_id == rel_id
    assert version.mutation_type == MutationType.CREATED

def test_change_event_invariants():
    repo_id = RepositoryId.generate()
    seid = SEID.generate()
    event_id = uuid.uuid4()
    
    event = ChangeEvent(
        id=event_id,
        repository_id=repo_id,
        commit_hash="hash1",
        seid=seid,
        change_type=MutationType.RENAMED,
        metadata={"old_name": "foo", "new_name": "bar"}
    )
    
    assert event.id == event_id
    assert event.change_type == MutationType.RENAMED
    assert event.metadata["old_name"] == "foo"
