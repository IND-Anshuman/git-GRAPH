import uuid
from src.infrastructure.extraction.compiler.compiler_context import CompilerContext
from src.domain.value_objects.semantic_type import SemanticType
from src.domain.value_objects.semantic_relationship_type import SemanticRelationshipType
from src.domain.value_objects.semantic_extraction_report import SemanticExtractionReport
from src.application.semantic.isr.canonical_entity import CanonicalEntity
from src.application.semantic.isr.canonical_relationship import CanonicalRelationship
from src.domain.value_objects.code_location import CodeLocation
from src.infrastructure.extraction.compiler.passes.base import ICompilerPass

class Pass9ISRGeneration(ICompilerPass):
    """Pass 9: ISR Generation. Assembles Canonical entities/relationships and outputs SemanticExtractionReport."""

    def execute(self, context: CompilerContext) -> None:
        semantic_types_set = set()
        
        # 1. Generate Canonical Entities
        for raw in context.raw_entities:
            role = context.inferred_roles.get(raw.name)
            if role:
                sem_type = SemanticType(
                    id=role.role_name.lower(),
                    category="architecture",
                    name=role.role_name,
                    parent_type=None
                )
            else:
                ent_type_name = getattr(raw.entity_type, "name", str(raw.entity_type))
                sem_type = SemanticType(
                    id=ent_type_name.lower(),
                    category="syntax",
                    name=ent_type_name,
                    parent_type=None
                )
            semantic_types_set.add(sem_type.name)
            
            entity_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{context.file_path}:{raw.name}"))
            
            location = CodeLocation(
                file_path=context.file_path,
                start_line=raw.start_line,
                end_line=raw.end_line,
                start_column=raw.start_column,
                end_column=raw.end_column
            )
            
            canonical_ent = CanonicalEntity(
                id=entity_id,
                name=raw.name,
                qualified_name=raw.name,
                entity_type=sem_type.name,
                decorators=raw.metadata.get("decorators", []),
                location=location,
                metadata=raw.metadata,
                semantic_type=sem_type
            )
            context.generated_entities.append(canonical_ent)
            
        # 2. Generate Canonical Relationships
        for rel in context.raw_relationships:
            rel_type_name = getattr(rel.relationship_type, "name", str(rel.relationship_type))
            sem_rel_type = SemanticRelationshipType(
                id=rel_type_name.lower(),
                category="syntax",
                name=rel_type_name,
                parent_type=None
            )
            
            src_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{context.file_path}:{rel.source_name}"))
            tgt_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{context.file_path}:{rel.target_name}"))
            
            conf_obj = context.relationships_confidence.get((rel.source_name, rel.target_name, rel_type_name))
            confidence_val = conf_obj.final_score if conf_obj else 0.8
            
            canonical_rel = CanonicalRelationship(
                id=str(uuid.uuid4()),
                from_entity_id=src_id,
                to_entity_id=tgt_id,
                relationship_type=sem_rel_type.name,
                confidence=confidence_val,
                properties=rel.metadata,
                semantic_relationship_type=sem_rel_type
            )
            context.generated_relationships.append(canonical_rel)
            
        # 3. Generate Report & Confidence Histogram
        all_confidences = [rel.confidence for rel in context.generated_relationships]
        all_confidences += [hint.confidence for hint in context.semantic_hints]
        
        histogram = {"0.0-0.2": 0.0, "0.2-0.4": 0.0, "0.4-0.6": 0.0, "0.6-0.8": 0.0, "0.8-1.0": 0.0}
        for c in all_confidences:
            if c <= 0.2:
                histogram["0.0-0.2"] += 1
            elif c <= 0.4:
                histogram["0.2-0.4"] += 1
            elif c <= 0.6:
                histogram["0.4-0.6"] += 1
            elif c <= 0.8:
                histogram["0.6-0.8"] += 1
            else:
                histogram["0.8-1.0"] += 1
                
        total_vals = len(all_confidences)
        if total_vals > 0:
            for k in histogram:
                histogram[k] = round(histogram[k] / total_vals, 2)
                
        context.report = SemanticExtractionReport(
            entities_found=len(context.generated_entities),
            relationships_found=len(context.generated_relationships),
            hints_found=len(context.semantic_hints),
            flows_found=len(context.flows),
            roles_found=len(context.inferred_roles),
            frameworks_detected=list(context.frameworks_detected),
            semantic_types_detected=list(semantic_types_set),
            capability_hints_found=len(context.capability_hints),
            architecture_hints_found=len(context.architecture_hints),
            confidence_histogram=histogram
        )
