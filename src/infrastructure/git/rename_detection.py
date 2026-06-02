"""Rename detection engine for identifying renamed entities."""

import difflib
from typing import List, Tuple
from src.domain.entities.code_entity import CodeEntity
from src.domain.value_objects.entity_id import SEID

class RenameDetector:
    """Detects when an entity has been renamed (distinguishing it from a delete + create)."""

    def __init__(self, threshold: float = 0.80) -> None:
        self.threshold = threshold

    def detect_renames(
        self,
        deleted_entities: List[CodeEntity],
        created_entities: List[CodeEntity]
    ) -> List[Tuple[SEID, CodeEntity, float]]:
        """Compares deleted and created entities and detects potential renames.
        
        Returns a list of tuples: (deleted_entity_seid, renamed_new_entity, confidence_score)
        """
        renames = []
        # Keep track of matched entities to avoid double assignment
        matched_created_seids = set()

        for deleted in deleted_entities:
            best_match = None
            best_score = 0.0

            for created in created_entities:
                if created.seid in matched_created_seids:
                    continue
                # Renames must preserve the entity type (e.g. a method can't rename to a class)
                if deleted.entity_type != created.entity_type:
                    continue

                score = self.calculate_similarity(deleted, created)
                if score > best_score and score >= self.threshold:
                    best_score = score
                    best_match = created

            if best_match:
                renames.append((deleted.seid, best_match, best_score))
                matched_created_seids.add(best_match.seid)

        return renames

    def calculate_similarity(self, a: CodeEntity, b: CodeEntity) -> float:
        """Calculates a similarity score between two entities from 0.0 to 1.0."""
        score = 0.0

        # 1. Structural Fingerprint Match (max +0.40)
        # If the abstract syntax tree structure is identical, it's a strong indicator
        if (a.structural_fingerprint and b.structural_fingerprint and 
            a.structural_fingerprint.value == b.structural_fingerprint.value):
            score += 0.40

        # 2. Content similarity of source code text (max +0.40)
        # If source text is available, compare them using difflib
        if a.source_text and b.source_text:
            text_ratio = difflib.SequenceMatcher(None, a.source_text, b.source_text).ratio()
            score += text_ratio * 0.40
        elif a.content_hash and b.content_hash and a.content_hash == b.content_hash:
            # If text is not available but content hash matches exactly
            score += 0.40

        # 3. Positional/Path context similarity (max +0.10)
        # If the entities are located in the same file or directory
        if a.location.file_path == b.location.file_path:
            score += 0.10
        else:
            # Directory path similarity
            a_dir = "/".join(a.location.file_path.split("/")[:-1])
            b_dir = "/".join(b.location.file_path.split("/")[:-1])
            if a_dir == b_dir:
                score += 0.05

        # 4. Scope context similarity (max +0.10)
        # If they share the same parent entity
        if a.parent_seid == b.parent_seid:
            score += 0.10

        return score
