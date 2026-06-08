"""Unit tests for Phase 4 ConceptExplanationEngine."""

import uuid
from datetime import datetime, timezone
import pytest

from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.enums.entity_type import EntityType
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.entity_id import SEID
from src.application.services.concept_explanation_engine import ConceptExplanationEngine


class MockLogicVersion:
    def __init__(self, id, code_entity_seid, logic_signature_id, commit_hash):
        self.id = id
        self.code_entity_seid = code_entity_seid
        self.logic_signature_id = logic_signature_id
        self.commit_hash = commit_hash
        self.overall_confidence = 0.94


class MockLogicSignature:
    def __init__(self, canonical_name, file_path):
        self.canonical_name = canonical_name
        self.file_path = file_path


class MockCodeEntity:
    def __init__(self, seid, entity_type):
        self.seid = SEID(seid) if isinstance(seid, str) else seid
        self.entity_type = entity_type


class MockEntityVersion:
    def __init__(self, file_path, start_line, end_line):
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line


class MockUow:
    def __init__(self, lvs, sigs, entities, entity_versions):
        self.lvs = lvs
        self.sigs = sigs
        self.entities = entities
        self._entity_versions = entity_versions

    @property
    def logic_versions(self):
        class MockLVRepo:
            def get_by_id(sub_self, lid):
                return self.lvs.get(lid)
        return MockLVRepo()

    @property
    def logic_signatures(self):
        class MockSigRepo:
            def get_by_id(sub_self, sid):
                return self.sigs.get(sid)
        return MockSigRepo()

    @property
    def code_entities(self):
        class MockEntityRepo:
            def get_by_seid(sub_self, seid):
                return self.entities.get(str(seid.value) if hasattr(seid, "value") else str(seid))
        return MockEntityRepo()

    @property
    def entity_versions(self):
        class MockEvRepo:
            def get_latest_before_or_at(sub_self, seid, commit):
                return self._entity_versions.get(str(seid.value) if hasattr(seid, "value") else str(seid))
        return MockEvRepo()


def test_concept_explanation_generation():
    repo_id = RepositoryId.generate()
    concept_id = uuid.uuid4()
    commit_hash = "hash1"
    now = datetime.now(timezone.utc)

    node = ConceptNode(concept_id, repo_id, "security.auth", "Authentication", "Authentication", True, now, now)
    version = ConceptVersion(uuid.uuid4(), concept_id, commit_hash, 1, 0.94, True, {}, now)

    lv1_id = uuid.uuid4()
    lv2_id = uuid.uuid4()

    ev1 = ConceptEvidence(uuid.uuid4(), version.id, "LOGIC_VERSION", lv1_id, 0.95, {}, now)
    ev2 = ConceptEvidence(uuid.uuid4(), version.id, "LOGIC_VERSION", lv2_id, 0.92, {}, now)

    class SEIDMock:
        def __init__(self, val):
            self.value = val

    lvs = {
        lv1_id: MockLogicVersion(lv1_id, SEIDMock("func:auth.verify_password"), uuid.uuid4(), commit_hash),
        lv2_id: MockLogicVersion(lv2_id, SEIDMock("func:jwt_helper.decode_token"), uuid.uuid4(), commit_hash),
    }

    sigs = {
        lvs[lv1_id].logic_signature_id: MockLogicSignature("auth_bcrypt_verification", "src/services/auth.py"),
        lvs[lv2_id].logic_signature_id: MockLogicSignature("auth_jwt_verification", "src/utils/jwt_helper.py"),
    }

    entities = {
        "func:auth.verify_password": MockCodeEntity("func:auth.verify_password", EntityType.FUNCTION),
        "func:jwt_helper.decode_token": MockCodeEntity("func:jwt_helper.decode_token", EntityType.FUNCTION),
    }

    entity_versions = {
        "func:auth.verify_password": MockEntityVersion("src/services/auth.py", 10, 30), # 21 LOC
        "func:jwt_helper.decode_token": MockEntityVersion("src/utils/jwt_helper.py", 5, 28), # 24 LOC
    }

    uow = MockUow(lvs, sigs, entities, entity_versions)

    engine = ConceptExplanationEngine()
    explanation = engine.explain_concept(uow, node, version, [ev1, ev2])

    assert explanation.concept_version_id == version.id
    # Check deterministic summary matching the expected format
    assert "Authentication capability is verified with high confidence (94%)" in explanation.summary
    assert "based on 2 active behavior patterns" in explanation.summary
    assert "across 2 files" in explanation.summary

    # Check footprint statistics inside detail
    footprint = explanation.detail["evidence_breakdown"]["structural_footprint"]
    assert footprint["file_count"] == 2
    assert footprint["function_count"] == 2
    assert footprint["loc_estimate"] == 45
