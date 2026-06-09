"""Semantic Evolution Engine to track temporal graph snapshots and calculate diffs bitemporally."""

import uuid
from typing import Any, Dict, List
from sqlalchemy import select, and_
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.services.historical_reconstruction import HistoricalReconstructionService
from src.domain.value_objects.repository_id import RepositoryId


class SemanticEvolutionEngine:
    """Tracks ontology mutations bitemporally and exposes snapshot and diffing query APIs."""

    def __init__(self, uow: IUnitOfWork, reconstructor: HistoricalReconstructionService):
        self.uow = uow
        self.reconstructor = reconstructor

    def graph_at_commit(self, repository_id: RepositoryId, commit_hash: str) -> Dict[str, Any]:
        """Reconstructs structural, behavioral, and conceptual graph snapshots for a given commit."""
        # 1. Reconstruct structural entities and relationships
        entities, relationships = self.reconstructor.reconstruct_graph_at_commit(
            self.uow, repository_id, commit_hash
        )

        active_logic_versions = []
        active_concepts = []
        active_concept_versions = []

        # 2. Query active behavior logic versions and concept snapshots
        with self.uow:
            from src.infrastructure.persistence.models.logic_models import LogicVersionModel
            from src.infrastructure.persistence.mappers.logic_mapper import LogicMapper
            
            stmt_l = select(LogicVersionModel).where(LogicVersionModel.commit_hash == commit_hash)
            models_l = self.uow._session.execute(stmt_l).scalars().all()
            active_logic_versions = [LogicMapper.to_logic_version_entity(m) for m in models_l]

            from src.infrastructure.persistence.models.concept_models import ConceptVersionModel
            from src.infrastructure.persistence.mappers.concept_mapper import ConceptMapper
            
            stmt_c = select(ConceptVersionModel).where(
                and_(
                    ConceptVersionModel.commit_hash == commit_hash,
                    ConceptVersionModel.is_active == True
                )
            )
            models_c = self.uow._session.execute(stmt_c).scalars().all()
            active_concept_versions = [ConceptMapper.to_concept_version_entity(m) for m in models_c]

            for cv in active_concept_versions:
                node = self.uow.concept_nodes.get_by_id(cv.concept_id)
                if node:
                    active_concepts.append(node)

        return {
            "entities": entities,
            "relationships": relationships,
            "behaviors": active_logic_versions,
            "concepts": active_concepts,
            "concept_versions": active_concept_versions,
        }

    def graph_diff(self, repository_id: RepositoryId, commit_a: str, commit_b: str) -> Dict[str, Any]:
        """Computes structural and taxonomic additions/removals between two commits."""
        state_a = self.graph_at_commit(repository_id, commit_a)
        state_b = self.graph_at_commit(repository_id, commit_b)

        # 1. Diff entities
        entities_a = {str(e.seid.value): e for e in state_a["entities"]}
        entities_b = {str(e.seid.value): e for e in state_b["entities"]}
        added_entities = [e for seid, e in entities_b.items() if seid not in entities_a]
        removed_entities = [e for seid, e in entities_a.items() if seid not in entities_b]

        # 2. Diff relationships
        rels_a = {str(r.id): r for r in state_a["relationships"]}
        rels_b = {str(r.id): r for r in state_b["relationships"]}
        added_relationships = [r for rid, r in rels_b.items() if rid not in rels_a]
        removed_relationships = [r for rid, r in rels_a.items() if rid not in rels_b]

        # 3. Diff behaviors
        behaviors_a = {str(v.logic_signature_id): v for v in state_a["behaviors"]}
        behaviors_b = {str(v.logic_signature_id): v for v in state_b["behaviors"]}
        added_behaviors = [v for sig_id, v in behaviors_b.items() if sig_id not in behaviors_a]
        removed_behaviors = [v for sig_id, v in behaviors_a.items() if sig_id not in behaviors_b]

        # 4. Diff concepts
        concepts_a = {str(c.id): c for c in state_a["concepts"]}
        concepts_b = {str(c.id): c for c in state_b["concepts"]}
        added_concepts = [c for cid, c in concepts_b.items() if cid not in concepts_a]
        removed_concepts = [c for cid, c in concepts_a.items() if cid not in concepts_b]

        return {
            "added_entities": added_entities,
            "removed_entities": removed_entities,
            "added_relationships": added_relationships,
            "removed_relationships": removed_relationships,
            "added_behaviors": added_behaviors,
            "removed_behaviors": removed_behaviors,
            "added_concepts": added_concepts,
            "removed_concepts": removed_concepts,
        }
