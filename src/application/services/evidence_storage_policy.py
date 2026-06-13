"""Service implementing the evidence storage pruning policies (HOT/WARM/COLD)."""

import os
import gzip
import json
import uuid
import logging
from datetime import datetime
from sqlalchemy import select, delete
from src.infrastructure.persistence.models.evidence_models import SEEEEvidenceModel, CompilerOutputModel

logger = logging.getLogger(__name__)

class EvidenceStoragePruningService:
    """Enforces HOT/WARM/COLD evidence storage policies."""
    
    def __init__(self, session_factory, archive_dir: str):
        self.session_factory = session_factory
        self.archive_dir = archive_dir
        os.makedirs(self.archive_dir, exist_ok=True)
        
    def prune_repository_evidence(self, repository_id: uuid.UUID) -> None:
        """Enforces HOT (last 50 commits remain in DB tables), WARM (commits 51-500 moved to backup db tables/compressed payload), and COLD (older than 500 commits archived to gzip files on disk)."""
        uow = self.session_factory()
        with uow:
            session = uow._session
            # 1. Get all unique commits for this repository that have evidence
            stmt = select(SEEEEvidenceModel.commit_hash).where(
                SEEEEvidenceModel.repository_id == repository_id
            ).distinct()
            commits = [row[0] for row in session.execute(stmt).fetchall()]
            
            if not commits:
                return
                
            # Get committing times or creation times to sort
            from src.infrastructure.persistence.models.commit_model import CommitModel
            commit_dates = []
            for c_hash in commits:
                c_stmt = select(CommitModel.timestamp).where(
                    CommitModel.repository_id == repository_id,
                    CommitModel.hash == c_hash
                )
                res = session.execute(c_stmt).scalar_one_or_none()
                committed_at = res if res else datetime.utcnow()
                commit_dates.append((c_hash, committed_at))
                
            # Sort newest first
            commit_dates.sort(key=lambda x: x[1], reverse=True)
            sorted_commits = [x[0] for x in commit_dates]
            
            hot_commits = set(sorted_commits[:50])
            warm_commits = set(sorted_commits[50:500])
            cold_commits = set(sorted_commits[500:])
            
            # WARM processing: compress large columns
            for c_hash in warm_commits:
                # seee_evidence
                seee_stmt = select(SEEEEvidenceModel).where(
                    SEEEEvidenceModel.repository_id == repository_id,
                    SEEEEvidenceModel.commit_hash == c_hash
                )
                seee_rows = session.execute(seee_stmt).scalars().all()
                for row in seee_rows:
                    if "warm_payload" not in row.provenance:
                        payload = {
                            "symbol_graph": row.symbol_graph,
                            "type_evidence": row.type_evidence,
                            "call_sites": row.call_sites,
                            "dependency_graph": row.dependency_graph,
                            "api_evidence": row.api_evidence,
                            "database_evidence": row.database_evidence,
                            "event_evidence": row.event_evidence,
                            "ai_evidence": row.ai_evidence,
                            "flow_signatures": row.flow_signatures,
                            "structure_signatures": row.structure_signatures,
                            "raw_signals": row.raw_signals,
                            "diagnostics": row.diagnostics,
                        }
                        compressed = gzip.compress(json.dumps(payload).encode('utf-8'))
                        provenance = dict(row.provenance)
                        provenance["warm_payload"] = compressed.hex()
                        row.provenance = provenance
                        row.symbol_graph = {}
                        row.type_evidence = []
                        row.call_sites = []
                        row.dependency_graph = {}
                        row.api_evidence = []
                        row.database_evidence = []
                        row.event_evidence = []
                        row.ai_evidence = []
                        row.flow_signatures = []
                        row.structure_signatures = []
                        row.raw_signals = []
                        row.diagnostics = []
                        session.add(row)
                        
                # compiler_outputs
                comp_stmt = select(CompilerOutputModel).where(
                    CompilerOutputModel.repository_id == repository_id,
                    CompilerOutputModel.commit_hash == c_hash
                )
                comp_rows = session.execute(comp_stmt).scalars().all()
                for row in comp_rows:
                    if "warm_payload" not in row.report:
                        payload = {
                            "generated_entities": row.generated_entities,
                            "generated_relationships": row.generated_relationships,
                            "frameworks_detected": row.frameworks_detected,
                            "semantic_hints": row.semantic_hints,
                        }
                        compressed = gzip.compress(json.dumps(payload).encode('utf-8'))
                        report = dict(row.report)
                        report["warm_payload"] = compressed.hex()
                        row.report = report
                        row.generated_entities = []
                        row.generated_relationships = []
                        row.frameworks_detected = []
                        row.semantic_hints = []
                        session.add(row)
            
            # COLD processing: serialize to gzip archive and delete
            for c_hash in cold_commits:
                seee_stmt = select(SEEEEvidenceModel).where(
                    SEEEEvidenceModel.repository_id == repository_id,
                    SEEEEvidenceModel.commit_hash == c_hash
                )
                seee_rows = session.execute(seee_stmt).scalars().all()
                
                comp_stmt = select(CompilerOutputModel).where(
                    CompilerOutputModel.repository_id == repository_id,
                    CompilerOutputModel.commit_hash == c_hash
                )
                comp_rows = session.execute(comp_stmt).scalars().all()
                
                if seee_rows or comp_rows:
                    archive_payload = {
                        "seee_evidence": [],
                        "compiler_outputs": []
                    }
                    
                    for row in seee_rows:
                        if "warm_payload" in row.provenance:
                            decompressed = gzip.decompress(bytes.fromhex(row.provenance["warm_payload"])).decode('utf-8')
                            data = json.loads(decompressed)
                        else:
                            data = {
                                "symbol_graph": row.symbol_graph,
                                "type_evidence": row.type_evidence,
                                "call_sites": row.call_sites,
                                "dependency_graph": row.dependency_graph,
                                "api_evidence": row.api_evidence,
                                "database_evidence": row.database_evidence,
                                "event_evidence": row.event_evidence,
                                "ai_evidence": row.ai_evidence,
                                "flow_signatures": row.flow_signatures,
                                "structure_signatures": row.structure_signatures,
                                "raw_signals": row.raw_signals,
                                "diagnostics": row.diagnostics,
                            }
                        data.update({
                            "id": str(row.id),
                            "file_id": str(row.file_id),
                            "repository_id": str(row.repository_id),
                            "file_path": row.file_path,
                            "commit_hash": row.commit_hash,
                            "provenance": row.provenance,
                            "created_at": row.created_at.isoformat()
                        })
                        archive_payload["seee_evidence"].append(data)
                        
                    for row in comp_rows:
                        if "warm_payload" in row.report:
                            decompressed = gzip.decompress(bytes.fromhex(row.report["warm_payload"])).decode('utf-8')
                            data = json.loads(decompressed)
                        else:
                            data = {
                                "generated_entities": row.generated_entities,
                                "generated_relationships": row.generated_relationships,
                                "frameworks_detected": row.frameworks_detected,
                                "semantic_hints": row.semantic_hints,
                            }
                        data.update({
                            "id": str(row.id),
                            "file_id": str(row.file_id),
                            "repository_id": str(row.repository_id),
                            "file_path": row.file_path,
                            "commit_hash": row.commit_hash,
                            "report": row.report,
                            "created_at": row.created_at.isoformat()
                        })
                        archive_payload["compiler_outputs"].append(data)
                        
                    archive_file_path = os.path.join(self.archive_dir, f"cold_evidence_{repository_id}_{c_hash}.json.gz")
                    with gzip.open(archive_file_path, "wt", encoding="utf-8") as f:
                        json.dump(archive_payload, f)
                        
                    for row in seee_rows:
                        session.delete(row)
                    for row in comp_rows:
                        session.delete(row)
            
            uow.commit()
