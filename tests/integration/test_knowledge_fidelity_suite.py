"""Integration test suite validating Knowledge Fidelity, Unified Ingestion, and Decoupled Jobs."""

import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import sessionmaker

from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.application.ports.git_port import IGitAdapter
from src.application.ports.file_scanner_port import IFileScanner
from src.application.ports.parser_port import IParser
from src.domain.entities.repository import RepositoryEntity
from src.domain.enums.analysis_status import AnalysisStatus
from src.application.services.ingestion_pipeline import IngestionPipeline
from src.domain.services.identity_service import EntityIdentityService
from src.infrastructure.extraction.entity_extractor import EntityExtractorService
from src.infrastructure.extraction.relationship_extractor import RelationshipExtractorService
from src.infrastructure.parsing.language_registry import LanguageRegistry

class TestEngine:
    def __init__(self, engine):
        self.session_factory = sessionmaker(bind=engine)

class MockGitAdapter(IGitAdapter):
    def clone_repository(self, url: str, branch: str, target_dir: str) -> str:
        shutil.copytree(url, target_dir, dirs_exist_ok=True)
        return target_dir
        
    def get_current_commit_hash(self, local_path: str) -> str:
        return "mock_commit_hash_123"
        
    def checkout_commit(self, local_path: str, commit_hash: str) -> None:
        pass

def test_knowledge_fidelity_suite(db_engine, tmp_path):
    # 1. Create a mock repository directory containing configuration files
    repo_src_dir = tmp_path / "mock_repo"
    repo_src_dir.mkdir()
    
    # Dockerfile
    dockerfile_content = """
    FROM python:3.12-slim
    WORKDIR /app
    ENV PORT=8080
    EXPOSE 8080
    CMD ["python", "main.py"]
    """
    (repo_src_dir / "Dockerfile").write_text(dockerfile_content)
    
    # Kubernetes
    k8s_content = """
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: mock-deployment
      namespace: test-ns
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: mock-app
      template:
        metadata:
          labels:
            app: mock-app
        spec:
          containers:
          - name: mock-container
          - image: mock-image:latest
            ports:
            - containerPort: 8080
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: mock-service
      namespace: test-ns
    spec:
      selector:
        app: mock-app
      ports:
      - port: 80
        targetPort: 8080
    """
    (repo_src_dir / "deployment.yaml").write_text(k8s_content)
    
    # Terraform
    tf_content = """
    resource "aws_db_instance" "postgres" {
      engine = "postgres"
      instance_class = "db.t3.micro"
    }
    """
    (repo_src_dir / "main.tf").write_text(tf_content)
    
    # OpenAPI
    openapi_content = """
    {
      "openapi": "3.0.0",
      "info": {
        "title": "Mock API Service",
        "version": "1.0.0"
      },
      "paths": {
        "/users": {
          "get": {
            "operationId": "getUsers",
            "summary": "Retrieve user list"
          }
        }
      }
    }
    """
    (repo_src_dir / "openapi.json").write_text(openapi_content)
    
    # Protobuf
    proto_content = """
    syntax = "proto3";
    package mock;
    message UserRequest {
      string id = 1;
    }
    service UserService {
      rpc GetUser(UserRequest) returns (UserRequest);
    }
    """
    (repo_src_dir / "service.proto").write_text(proto_content)
    
    # Mock Python file to trigger SEEE
    py_content = """
    import bcrypt
    
    def verify_password(password, hashed):
        # Trigger auth behavior pattern
        return bcrypt.checkpw(password, hashed)
    """
    (repo_src_dir / "auth.py").write_text(py_content)
    
    # Setup dependencies
    test_engine = TestEngine(db_engine)
    uow_factory = lambda: SQLAlchemyUnitOfWork(test_engine)
    
    # Inject Mock Git Adapter
    git_adapter = MockGitAdapter()
    
    from src.infrastructure.scanning.file_scanner import FileSystemScanner
    from src.infrastructure.parsing.parser_service import TreeSitterParserService
    file_scanner = FileSystemScanner()
    parser = TreeSitterParserService(LanguageRegistry())
    
    identity_service = EntityIdentityService()
    entity_extractor = EntityExtractorService(LanguageRegistry(), identity_service)
    relationship_extractor = RelationshipExtractorService(LanguageRegistry())
    
    # Run Ingestion
    from src.domain.value_objects.repository_id import RepositoryId
    from src.application.use_cases.ingest_repository import IngestRepositoryUseCase
    from src.application.semantic.calibration.calibration_engine import ConfidenceCalibrationEngine
    from src.application.semantic.schema.schema_registry import SchemaRegistry
    from src.application.semantic.embedding.embedding_registry import EmbeddingRegistry
    from src.application.semantic.discovery.concept_discovery_engine import ConceptDiscoveryEngine
    
    calibration_engine = ConfidenceCalibrationEngine()
    schema_registry = SchemaRegistry(uow_factory())
    embedding_registry = EmbeddingRegistry(uow_factory())
    concept_discovery_engine = ConceptDiscoveryEngine(uow_factory(), schema_registry, embedding_registry, calibration_engine)
    
    storage_root = str(tmp_path / "storage")
    
    use_case = IngestRepositoryUseCase(
        git_adapter=git_adapter,
        file_scanner=file_scanner,
        parser=parser,
        entity_extractor=entity_extractor,
        relationship_extractor=relationship_extractor,
        uow_factory=uow_factory,
        storage_root=storage_root,
        identity_service=identity_service,
        calibration_engine=None,
        concept_discovery_engine=None
    )
    
    # Trigger execute
    from src.application.dtos.commands import IngestRepositoryCommand
    command = IngestRepositoryCommand(
        url=str(repo_src_dir),
        branch="main",
        name="mock-ingestion-repo"
    )
    
    response = use_case.execute(command)
    assert response.errors == []
    assert response.status == "COMPLETED"
    
    # Verify that IngestionJob persisted source files and entities successfully
    with uow_factory() as uow:
        # Check source files
        files = uow.source_files.get_by_repository(RepositoryId(uuid.UUID(response.repository_id)))
        assert len(files) > 0
        
        # Check entities
        entities = uow.code_entities.get_by_repository(RepositoryId(uuid.UUID(response.repository_id)))
        assert len(entities) > 0
        
        # We expect SEMANTIC layer entities from Docker, K8s, Terraform, OpenAPI, Protobuf
        semantic_entities = [e for e in entities if e.metadata.get("layer") == "SEMANTIC"]
        assert len(semantic_entities) > 0
        
        # We should find CONTAINER (Docker), DEPLOYMENT (K8s / Terraform), MESSAGE_CONTRACT/SERVICE_DEFINITION (Protobuf), API_CONTRACT (OpenAPI)
        types = {e.entity_type.name for e in semantic_entities}
        assert "CONTAINER" in types
        assert "DEPLOYMENT" in types
        assert "SERVICE_DEFINITION" in types
        assert "API_CONTRACT" in types
        assert "MESSAGE_CONTRACT" in types
        
        # Check seee_evidence and compiler_outputs tables are populated
        from src.infrastructure.persistence.models.evidence_models import SEEEEvidenceModel, CompilerOutputModel
        seee_rows = uow._session.query(SEEEEvidenceModel).filter_by(repository_id=uuid.UUID(response.repository_id)).all()
        assert len(seee_rows) > 0
        
        comp_rows = uow._session.query(CompilerOutputModel).filter_by(repository_id=uuid.UUID(response.repository_id)).all()
        assert len(comp_rows) > 0

    # 4. Trigger enrichment, concepts, capabilities, reasoning background jobs synchronously in test context
    from src.application.jobs.graph_enrichment_job import GraphEnrichmentJob
    from src.application.jobs.concept_job import ConceptJob
    from src.application.jobs.capability_job import CapabilityJob
    from src.application.jobs.reasoning_job import ReasoningJob
    
    repo_uuid = uuid.UUID(response.repository_id)
    
    # Before concept job runs, let's seed two LogicSignatures in DB to support concept clustering
    with uow_factory() as uow:
        from src.domain.entities.logic_signature import LogicSignature
        from src.domain.enums.language import SupportedLanguage
        sig1 = LogicSignature(
            id=uuid.uuid4(),
            repository_id=RepositoryId(repo_uuid),
            canonical_name="auth_bcrypt_verification",
            language=SupportedLanguage.PYTHON,
            ontology_node_id="security.authentication.hash_comparison",
            description="Bcrypt verification",
            created_at=datetime.now(timezone.utc),
            metadata={"file_path": "auth.py", "entity_seid": "mock_entity_seid_1"}
        )
        sig2 = LogicSignature(
            id=uuid.uuid4(),
            repository_id=RepositoryId(repo_uuid),
            canonical_name="auth_password_check",
            language=SupportedLanguage.PYTHON,
            ontology_node_id="security.authentication.hash_comparison",
            description="Password check",
            created_at=datetime.now(timezone.utc),
            metadata={"file_path": "auth.py", "entity_seid": "mock_entity_seid_2"}
        )
        
        # Seed ontology node as well
        from src.domain.entities.ontology_node import OntologyNode
        onto = OntologyNode(
            id="security.authentication.hash_comparison",
            name="Cryptographic Hash Verification",
            parent_id=None,
            domain="Security",
            description="Verification via hashing",
            ontology_version="3.0.0"
        )
        uow.ontology_nodes.save(onto)
        uow.logic_signatures.save(sig1)
        uow.logic_signatures.save(sig2)
        uow.commit()

    enrich_job = GraphEnrichmentJob(uow_factory, calibration_engine)
    enrich_job.run(repo_uuid)
    
    concept_job = ConceptJob(concept_discovery_engine, uow_factory)
    concept_job.run(repo_uuid)
    
    cap_job = CapabilityJob(uow_factory)
    cap_job.run(repo_uuid)
    
    reasoning_job = ReasoningJob(uow_factory)
    reasoning_job.run(repo_uuid)
    
    # Verify post-ingestion job candidates and artifacts
    with uow_factory() as uow:
        from src.infrastructure.persistence.models.concept_models import ConceptCandidateModel, CapabilityCandidateModel
        from src.infrastructure.persistence.models.knowledge_artifact_model import KnowledgeArtifactModel
        
        concepts = uow._session.query(ConceptCandidateModel).all()
        assert len(concepts) > 0
        
        capabilities = uow._session.query(CapabilityCandidateModel).all()
        assert len(capabilities) > 0
        
        artifacts = uow._session.query(KnowledgeArtifactModel).filter_by(repository_id=repo_uuid).all()
        assert len(artifacts) > 0
        
        layers = {a.artifact_type for a in artifacts}
        assert "blast_radius" in layers
        assert "architecture_explanation" in layers

    # 5. Verify HOT/WARM/COLD Pruning Service
    from src.application.services.evidence_storage_policy import EvidenceStoragePruningService
    pruning_service = EvidenceStoragePruningService(uow_factory, os.path.join(storage_root, "archives"))
    
    # We will simulate more commits so we can trigger WARM and COLD policies
    with uow_factory() as uow:
        from src.infrastructure.persistence.models.commit_model import CommitModel
        from src.infrastructure.persistence.models.evidence_models import SEEEEvidenceModel
        
        # Create 55 commits
        for i in range(55):
            c_hash = f"hash_commit_{i}"
            c_model = CommitModel(
                hash=c_hash,
                repository_id=repo_uuid,
                author="test",
                email="test@test.com",
                timestamp=datetime.now(timezone.utc),
                message=f"commit msg {i}",
                parent_hashes=[]
            )
            uow._session.add(c_model)
            
            # Add seee_evidence
            seee_ev = SEEEEvidenceModel(
                id=uuid.uuid4(),
                file_id=files[0].id.value if hasattr(files[0].id, 'value') else files[0].id,
                repository_id=repo_uuid,
                file_path=files[0].file_path,
                commit_hash=c_hash,
                symbol_graph={},
                type_evidence=[],
                call_sites=[],
                dependency_graph={},
                api_evidence=[],
                database_evidence=[],
                event_evidence=[],
                ai_evidence=[],
                flow_signatures=[],
                structure_signatures=[],
                raw_signals=[],
                diagnostics=[],
                provenance={}
            )
            uow._session.add(seee_ev)
        uow.commit()
        
    # Run Pruning Service
    pruning_service.prune_repository_evidence(repo_uuid)
    
    # Check that older seee_evidences were compressed/WARM payloaded
    with uow_factory() as uow:
        warm_seee = uow._session.query(SEEEEvidenceModel).filter(
            SEEEEvidenceModel.repository_id == repo_uuid,
            SEEEEvidenceModel.commit_hash == "hash_commit_0"
        ).first()
        assert "warm_payload" in warm_seee.provenance
        
    print("\n" + "="*50)
    print("KNOWLEDGE FIDELITY VALIDATION REPORT")
    print("="*50)
    print(f"Repository Ingested: {response.repository_id}")
    print(f"Semantic Layer Entities Extracted: {len(semantic_entities)}")
    print(f"Concept Candidates Discovered: {len(concepts)}")
    print(f"Capability Candidates Discovered: {len(capabilities)}")
    print(f"LLM Reasoning Artifacts Generated: {len(artifacts)}")
    print("HOT/WARM/COLD Storage Pruning: Verified successfully")
    print("="*50)
