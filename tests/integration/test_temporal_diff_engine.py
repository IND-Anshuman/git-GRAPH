"""Integration tests for temporal diff, rename, and move detection."""

import uuid
from src.domain.entities.code_entity import CodeEntity
from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.domain.value_objects.fingerprint import StructuralFingerprint
from src.infrastructure.git.commit_walker import GitFileChange
from src.infrastructure.git.rename_detection import RenameDetector
from src.infrastructure.git.move_detection import MoveDetector
from src.infrastructure.git.temporal_diff_engine import TemporalDiffEngine, DiffResult
from src.domain.enums.mutation_type import MutationType

def test_exact_match_and_modification():
    repo_id = RepositoryId.generate()
    file_id = FileId(uuid.uuid4())
    seid = SEID.generate()
    
    # 1. Previous state (Graph A)
    prev_entity = CodeEntity(
        seid=seid,
        entity_type=EntityType.FUNCTION,
        name="hello",
        qualified_name="hello",
        file_id=file_id,
        repository_id=repo_id,
        parent_seid=None,
        language=SupportedLanguage.PYTHON,
        location=CodeLocation("src/hello.py", 1, 5, 0, 0),
        content_hash="hash_v1",
        structural_fingerprint=StructuralFingerprint("fp_v1"),
        source_text="def hello(): pass",
        metadata={"version_count": 1}
    )
    
    # 2. Current state (Graph B) - Content hash changed (modified)
    curr_entity = CodeEntity(
        seid=SEID.generate(), # temporary ID
        entity_type=EntityType.FUNCTION,
        name="hello",
        qualified_name="hello",
        file_id=FileId(uuid.uuid4()),
        repository_id=repo_id,
        parent_seid=None,
        language=SupportedLanguage.PYTHON,
        location=CodeLocation("src/hello.py", 1, 5, 0, 0),
        content_hash="hash_v2",
        structural_fingerprint=StructuralFingerprint("fp_v2"),
        source_text="def hello(): print('hi')",
        metadata={}
    )
    
    detector_rename = RenameDetector()
    detector_move = MoveDetector()
    engine = TemporalDiffEngine(detector_rename, detector_move)
    
    diff = engine.compute_diff(
        repository_id=repo_id,
        commit_hash="hash_commit",
        previous_entities=[prev_entity],
        previous_relationships=[],
        current_entities=[curr_entity],
        current_relationships=[],
        file_changes=[GitFileChange("src/hello.py", "modified")]
    )
    
    # Assertions
    assert len(diff.versions_to_save) == 1
    assert diff.versions_to_save[0].seid == seid # SEID resolved to prev
    assert diff.versions_to_save[0].mutation_type == MutationType.MODIFIED
    assert diff.versions_to_save[0].version_ordinal == 2
    
    assert len(diff.change_events_to_save) == 1
    assert diff.change_events_to_save[0].change_type == MutationType.MODIFIED

def test_move_detection_resolution():
    repo_id = RepositoryId.generate()
    old_file_id = FileId(uuid.uuid4())
    seid = SEID.generate()
    
    # Old Entity
    prev_entity = CodeEntity(
        seid=seid,
        entity_type=EntityType.CLASS,
        name="Worker",
        qualified_name="Worker",
        file_id=old_file_id,
        repository_id=repo_id,
        parent_seid=None,
        language=SupportedLanguage.PYTHON,
        location=CodeLocation("src/old_path.py", 1, 10, 0, 0),
        content_hash="same_hash",
        structural_fingerprint=StructuralFingerprint("same_fp"),
        source_text="class Worker: pass",
        metadata={"version_count": 1}
    )
    
    # New Entity in moved file
    curr_entity = CodeEntity(
        seid=SEID.generate(),
        entity_type=EntityType.CLASS,
        name="Worker",
        qualified_name="Worker",
        file_id=FileId(uuid.uuid4()),
        repository_id=repo_id,
        parent_seid=None,
        language=SupportedLanguage.PYTHON,
        location=CodeLocation("src/new_path.py", 1, 10, 0, 0),
        content_hash="same_hash",
        structural_fingerprint=StructuralFingerprint("same_fp"),
        source_text="class Worker: pass",
        metadata={}
    )
    
    detector_rename = RenameDetector()
    detector_move = MoveDetector()
    engine = TemporalDiffEngine(detector_rename, detector_move)
    
    diff = engine.compute_diff(
        repository_id=repo_id,
        commit_hash="hash_commit",
        previous_entities=[prev_entity],
        previous_relationships=[],
        current_entities=[curr_entity],
        current_relationships=[],
        file_changes=[GitFileChange("src/new_path.py", "renamed", old_path="src/old_path.py")]
    )
    
    assert len(diff.versions_to_save) == 1
    assert diff.versions_to_save[0].seid == seid
    assert diff.versions_to_save[0].mutation_type == MutationType.MOVED
    assert diff.versions_to_save[0].version_ordinal == 2

def test_rename_detection_resolution():
    repo_id = RepositoryId.generate()
    file_id = FileId(uuid.uuid4())
    seid = SEID.generate()
    
    prev_entity = CodeEntity(
        seid=seid,
        entity_type=EntityType.FUNCTION,
        name="calculate_tax",
        qualified_name="calculate_tax",
        file_id=file_id,
        repository_id=repo_id,
        parent_seid=None,
        language=SupportedLanguage.PYTHON,
        location=CodeLocation("src/tax.py", 1, 10, 0, 0),
        content_hash="same_hash",
        structural_fingerprint=StructuralFingerprint("same_fp"),
        source_text="def calculate_tax(): pass",
        metadata={"version_count": 1}
    )
    
    curr_entity = CodeEntity(
        seid=SEID.generate(),
        entity_type=EntityType.FUNCTION,
        name="compute_tax", # name changed
        qualified_name="compute_tax",
        file_id=file_id,
        repository_id=repo_id,
        parent_seid=None,
        language=SupportedLanguage.PYTHON,
        location=CodeLocation("src/tax.py", 1, 10, 0, 0),
        content_hash="same_hash",
        structural_fingerprint=StructuralFingerprint("same_fp"),
        source_text="def compute_tax(): pass",
        metadata={}
    )
    
    detector_rename = RenameDetector()
    detector_move = MoveDetector()
    engine = TemporalDiffEngine(detector_rename, detector_move)
    
    diff = engine.compute_diff(
        repository_id=repo_id,
        commit_hash="hash_commit",
        previous_entities=[prev_entity],
        previous_relationships=[],
        current_entities=[curr_entity],
        current_relationships=[],
        file_changes=[GitFileChange("src/tax.py", "modified")]
    )
    
    assert len(diff.versions_to_save) == 1
    assert diff.versions_to_save[0].seid == seid
    assert diff.versions_to_save[0].mutation_type == MutationType.RENAMED
    assert diff.versions_to_save[0].version_ordinal == 2
