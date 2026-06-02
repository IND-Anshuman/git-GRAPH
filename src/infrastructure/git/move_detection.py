"""Move detection engine for tracking file and folder movement."""

from typing import List, Dict, Optional
from src.domain.entities.code_entity import CodeEntity
from src.infrastructure.git.commit_walker import GitFileChange

class MoveDetector:
    """Detects when an entity's file or folder has been moved or renamed in git."""

    def __init__(self, threshold: float = 0.90) -> None:
        self.threshold = threshold

    def build_file_move_map(self, file_changes: List[GitFileChange]) -> Dict[str, str]:
        """Creates a mapping from old_path -> new_path for renamed/moved files."""
        move_map = {}
        for change in file_changes:
            if change.change_type == "renamed" and change.old_path:
                move_map[change.old_path] = change.path
        return move_map

    def associate_moved_entities(
        self,
        deleted_entities: List[CodeEntity],
        created_entities: List[CodeEntity],
        file_move_map: Dict[str, str]
    ) -> List[tuple[CodeEntity, CodeEntity]]:
        """Identifies entities that were moved because their containing file or folder was relocated.
        
        Returns a list of tuples: (deleted_old_entity, created_new_entity)
        """
        associations = []
        
        # Helper to find if a file path belongs to a moved directory
        def get_mapped_path(old_path: str) -> Optional[str]:
            # Exact match in file_move_map
            if old_path in file_move_map:
                return file_move_map[old_path]
                
            # Folder-level move: check if any directory prefix is renamed
            for old_dir, new_dir in file_move_map.items():
                # Check if old_path starts with old_dir + "/"
                if old_path.startswith(old_dir + "/"):
                    relative_part = old_path[len(old_dir) + 1:]
                    return f"{new_dir}/{relative_part}"
            return None

        matched_created_seids = set()
        for deleted in deleted_entities:
            # Determine if this entity's file was moved
            mapped_file = get_mapped_path(deleted.location.file_path)
            if not mapped_file:
                continue

            # Look for a matching entity in the new file path
            # It must have the same name, type, and parent containment
            for created in created_entities:
                if created.seid in matched_created_seids:
                    continue
                if (created.location.file_path == mapped_file and
                    created.name == deleted.name and
                    created.entity_type == deleted.entity_type):
                    
                    associations.append((deleted, created))
                    matched_created_seids.add(created.seid)
                    break

        return associations
