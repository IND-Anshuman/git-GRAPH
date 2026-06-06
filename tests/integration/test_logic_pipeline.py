"""Integration tests for Phase 3 logic persistence and orchestration pipeline."""

import uuid
from datetime import datetime, timezone
import pytest

from src.domain.entities.repository import RepositoryEntity
from src.domain.entities.commit import Commit
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.entity_version import EntityVersion
from src.domain.entities.logic_signature import LogicSignature
from src.domain.entities.logic_version import LogicVersion
from src.domain.entities.logic_evidence import LogicEvidence
from src.domain.entities.logic_transition import LogicTransition
from src.domain.entities.behavior_explanation import BehaviorExplanation, RuleVerdict
from src.domain.entities.behavior_drift import BehaviorDrift
from src.domain.entities.behavior_pattern import BehaviorPattern
from src.domain.entities.ontology_node import OntologyNode
from src.domain.entities.logic_cluster import LogicCluster
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.domain.enums.mutation_type import MutationType
from src.domain.enums.evidence_type import EvidenceType
from src.domain.enums.transition_type import TransitionType
from src.domain.enums.drift_category import DriftCategory
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.domain.value_objects.logic_fingerprint import LogicFingerprint
from src.domain.value_objects.confidence_breakdown import ConfidenceBreakdown
from src.domain.value_objects.drift_dimensions import DriftDimensions
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork


class DummyEngine:
    def __init__(self, session):
        self.session_factory = lambda: session


def test_logic_pipeline_persistence_flow(db_session):
    uow = SQLAlchemyUnitOfWork(DummyEngine(db_session))
    repo_id = RepositoryId.generate()
    now = datetime.now(timezone.utc)
    
    with uow:
        # 1. Setup repository, commits, and entity versions
        repo = RepositoryEntity(
            id=repo_id,
            url="https://github.com/test/repo",
            name="test-repo",
            default_branch="main",
            local_path="src/",
            status=AnalysisStatus.COMPLETED,
            created_at=now,
            updated_at=now
        )
        uow.repositories.save(repo)
        
        commit1 = Commit("hash1", repo_id, "Auth", "email", now, "C1", [])
        commit2 = Commit("hash2", repo_id, "Auth", "email", now, "C2", ["hash1"])
        uow.commits.save(commit1)
        uow.commits.save(commit2)
        
        seid1 = SEID.generate()
        file_id = FileId(uuid.uuid4())
        entity = CodeEntity(
            seid=seid1,
            entity_type=EntityType.FUNCTION,
            name="verify_pass",
            qualified_name="verify_pass",
            file_id=file_id,
            repository_id=repo_id,
            parent_seid=None,
            language=SupportedLanguage.PYTHON,
            location=CodeLocation("src/auth.py", 1, 10, 0, 0)
        )
        uow.code_entities.save(entity)
        
        ev1 = EntityVersion(
            id=uuid.uuid4(),
            seid=seid1,
            commit_hash="hash1",
            version_ordinal=1,
            mutation_type=MutationType.CREATED,
            canonical_name="verify_pass",
            file_path="src/auth.py",
            start_line=1,
            end_line=10,
            content_hash="h1",
            structural_fingerprint="fp1"
        )
        ev2 = EntityVersion(
            id=uuid.uuid4(),
            seid=seid1,
            commit_hash="hash2",
            version_ordinal=2,
            mutation_type=MutationType.MODIFIED,
            canonical_name="verify_pass",
            file_path="src/auth.py",
            start_line=1,
            end_line=10,
            content_hash="h2",
            structural_fingerprint="fp2"
        )
        uow.entity_versions.save(ev1)
        uow.entity_versions.save(ev2)
        
        # 2. Setup OntologyNode and BehaviorPattern in DB
        onto_node = OntologyNode(
            id="security.authentication.hash_comparison",
            name="Cryptographic Hash Verification",
            parent_id=None,
            domain="Security",
            description="Verification via hashing",
            ontology_version="3.0.0"
        )
        uow.ontology_nodes.save(onto_node)
        
        pattern = BehaviorPattern(
            id=uuid.uuid4(),
            pattern_id="auth_bcrypt_verification",
            name="Bcrypt Verification",
            ontology_node_id="security.authentication.hash_comparison",
            base_confidence=0.95,
            pattern_version="1.0.0",
            schema_version="1.0",
            rules={"call": "bcrypt.checkpw"},
            index_keys=["call:bcrypt.checkpw", "import:bcrypt"],
            is_active=True,
            loaded_at=now
        )
        uow.behavior_patterns.save(pattern)
        
        # 3. Create and Save LogicSignature
        sig_id = uuid.uuid4()
        sig = LogicSignature(
            id=sig_id,
            repository_id=repo_id,
            canonical_name="auth_bcrypt_verification",
            language=SupportedLanguage.PYTHON,
            ontology_node_id="security.authentication.hash_comparison",
            description="Bcrypt verification",
            created_at=now,
            metadata={}
        )
        uow.logic_signatures.save(sig)
        
        # 4. Create and Save LogicVersion 1
        ver1_id = uuid.uuid4()
        fp1 = LogicFingerprint.compute("s1", "d1", "b1")
        cb1 = ConfidenceBreakdown.compute(1.0, 1.0, 1.0, 1.0, 1.0, 2)
        ver1 = LogicVersion(
            id=ver1_id,
            logic_signature_id=sig_id,
            code_entity_seid=seid1,
            commit_hash="hash1",
            version_ordinal=1,
            fingerprint=fp1,
            overall_confidence=0.95,
            confidence_breakdown=cb1,
            is_primary=True,
            metadata={"source_file": "src/auth.py"},
            created_at=now
        )
        uow.logic_versions.save(ver1)
        
        # Save logic evidence for version 1
        evid1 = LogicEvidence(
            id=uuid.uuid4(),
            logic_version_id=ver1_id,
            evidence_type=EvidenceType.AST_CALL,
            file_path="src/auth.py",
            start_line=5,
            end_line=5,
            ast_node_type="Call",
            matched_symbol="bcrypt.checkpw",
            matched_rule_id="r1",
            call_chain=["verify_pass", "checkpw"],
            confidence_contribution=0.50,
            metadata={},
            detected_at=now
        )
        uow.logic_evidence.save_batch([evid1])
        
        # Save explanation for version 1
        expl1 = BehaviorExplanation(
            id=uuid.uuid4(),
            logic_version_id=ver1_id,
            behavior_name="Bcrypt Verification",
            ontology_path="security.authentication.hash_comparison",
            overall_confidence=0.95,
            confidence_breakdown=cb1,
            matched_pattern_ids=["auth_bcrypt_verification"],
            evidence_summary="Matched bcrypt",
            rule_verdicts=[
                RuleVerdict(rule_id="r1", rule_description="bcrypt call", passed=True, contribution=0.50, evidence_ref=evid1.id)
            ],
            is_stale=False,
            generated_at=now,
            metadata={}
        )
        uow.behavior_explanations.save(expl1)
        
        # 5. Create and Save LogicVersion 2 (evolved version)
        ver2_id = uuid.uuid4()
        fp2 = LogicFingerprint.compute("s2", "d2", "b2")
        cb2 = ConfidenceBreakdown.compute(1.0, 1.0, 1.0, 1.0, 1.0, 2)
        ver2 = LogicVersion(
            id=ver2_id,
            logic_signature_id=sig_id,
            code_entity_seid=seid1,
            commit_hash="hash2",
            version_ordinal=2,
            fingerprint=fp2,
            overall_confidence=0.95,
            confidence_breakdown=cb2,
            is_primary=True,
            metadata={"source_file": "src/auth.py"},
            created_at=now
        )
        uow.logic_versions.save(ver2)
        
        # Save transition from v1 to v2
        trans_id = uuid.uuid4()
        trans = LogicTransition(
            id=trans_id,
            from_logic_version_id=ver1_id,
            to_logic_version_id=ver2_id,
            transition_type=TransitionType.EVOLVED,
            similarity_score=0.80,
            overall_confidence=0.95,
            metadata={},
            created_at=now
        )
        uow.logic_transitions.save(trans)
        
        # Save behavior drift
        drift_dims = DriftDimensions(0.20, 0.20, 0.0, 0.0, 0.0, 0.0)
        drift = BehaviorDrift(
            id=uuid.uuid4(),
            logic_transition_id=trans_id,
            from_logic_version_id=ver1_id,
            to_logic_version_id=ver2_id,
            drift_score=0.20,
            drift_category=DriftCategory.MINOR,
            dimension_scores=drift_dims,
            ontology_changed=False,
            security_boundary_crossed=False,
            computed_at=now,
            metadata={}
        )
        uow.behavior_drift.save(drift)
        
        # Save logic cluster
        cluster_id = uuid.uuid4()
        cluster = LogicCluster(
            id=cluster_id,
            name="Auth Cluster",
            category="Security",
            logic_signature_ids=[sig_id]
        )
        uow.logic_clusters.save(cluster)
        
        uow.commit()

    # 6. Retrieve and verify
    with uow:
        # Retrieve LogicSignature
        db_sig = uow.logic_signatures.get_by_id(sig_id)
        assert db_sig is not None
        assert db_sig.canonical_name == "auth_bcrypt_verification"
        assert db_sig.ontology_node_id == "security.authentication.hash_comparison"
        
        # Retrieve LogicVersions
        versions = uow.logic_versions.list_by_signature(sig_id)
        assert len(versions) == 2
        assert {v.id for v in versions} == {ver1_id, ver2_id}
        
        timeline = uow.logic_versions.get_by_entity_at_commit(seid1, "hash1")
        assert len(timeline) == 1
        assert timeline[0].id == ver1_id
        
        # Retrieve Evidence
        evs = uow.logic_evidence.get_by_logic_version(ver1_id)
        assert len(evs) == 1
        assert evs[0].matched_symbol == "bcrypt.checkpw"
        assert evs[0].call_chain == ["verify_pass", "checkpw"]
        
        # Retrieve Explanation
        expl = uow.behavior_explanations.get_by_logic_version(ver1_id)
        assert expl is not None
        assert expl.behavior_name == "Bcrypt Verification"
        assert len(expl.rule_verdicts) == 1
        assert expl.rule_verdicts[0].rule_description == "bcrypt call"
        
        # Retrieve Transition & Drift
        db_trans = uow.logic_transitions.get_by_from_version(ver1_id)
        assert len(db_trans) == 1
        assert db_trans[0].id == trans_id
        
        db_drift = uow.behavior_drift.get_by_transition(trans_id)
        assert db_drift is not None
        assert db_drift.drift_category == DriftCategory.MINOR
        
        # Retrieve Cluster
        db_cluster = uow.logic_clusters.get_by_id(cluster_id)
        assert db_cluster is not None
        assert db_cluster.name == "Auth Cluster"
        assert sig_id in db_cluster.logic_signature_ids
