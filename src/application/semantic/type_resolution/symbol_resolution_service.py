"""Service for repository-wide qualified name and symbol resolution, supporting incremental updates."""

from typing import Dict, List, Optional, Set, Tuple
import uuid

class IncrementalSymbolIndex:
    """In-memory cache mapping files to their exported symbols and declared imports."""

    def __init__(self) -> None:
        self.file_symbols: Dict[str, Set[str]] = {}  # file_path -> Set of fully qualified local names
        self.file_imports: Dict[str, Dict[str, Tuple[str, Optional[str]]]] = {}  # file_path -> {alias/name -> (source_module, original_name)}
        self.inheritance_map: Dict[str, Set[str]] = {}  # child_qname -> Set of parent_qnames
        self.symbol_details: Dict[str, Dict[str, Any]] = {}  # qname -> dict metadata (entity_type, name, file_path, etc.)

    def clear_file(self, file_path: str) -> None:
        """Clear all entries registered by a specific file (for incremental updates)."""
        if file_path in self.file_symbols:
            for qname in self.file_symbols[file_path]:
                self.symbol_details.pop(qname, None)
                self.inheritance_map.pop(qname, None)
            del self.file_symbols[file_path]
        self.file_imports.pop(file_path, None)

    def register_symbol(self, qname: str, file_path: str, details: Dict[str, Any]) -> None:
        if file_path not in self.file_symbols:
            self.file_symbols[file_path] = set()
        self.file_symbols[file_path].add(qname)
        self.symbol_details[qname] = details

    def register_import(self, file_path: str, name_or_alias: str, source_module: str, original_name: Optional[str] = None) -> None:
        if file_path not in self.file_imports:
            self.file_imports[file_path] = {}
        self.file_imports[file_path][name_or_alias] = (source_module, original_name)

    def register_inheritance(self, child_qname: str, parent_qname: str) -> None:
        if child_qname not in self.inheritance_map:
            self.inheritance_map[child_qname] = set()
        self.inheritance_map[child_qname].add(parent_qname)


class SymbolResolutionService:
    """Repository-wide symbol resolution engine handling namespaces, aliases, and imports."""

    def __init__(self, index: Optional[IncrementalSymbolIndex] = None) -> None:
        self.index = index or IncrementalSymbolIndex()

    def clear_file_cache(self, file_path: str) -> None:
        """Invalidate cache for a file before re-extracting it."""
        self.index.clear_file(file_path)

    def register_local_symbols(self, file_path: str, entities: List[Any]) -> None:
        """Populate local symbols in index."""
        for ent in entities:
            # ent can be a RawEntity or CodeEntity
            name = getattr(ent, "name", "")
            parent_name = getattr(ent, "parent_name", None)
            if not parent_name and hasattr(ent, "parent_seid") and ent.parent_seid:
                # Resolve parent_name if it is a CodeEntity
                parent_name = None # Fallback or keep it simple
            
            ent_type_str = getattr(getattr(ent, "entity_type", None), "name", str(getattr(ent, "entity_type", None)))
            
            # Simple dotted qualified name calculation
            qname = f"{parent_name}.{name}" if parent_name else name
            
            details = {
                "name": name,
                "entity_type": ent_type_str,
                "file_path": file_path,
                "parent_name": parent_name,
                "qname": qname
            }
            self.index.register_symbol(qname, file_path, details)

    def register_file_imports(self, file_path: str, relationships: List[Any]) -> None:
        """Index imports declared in a file."""
        for rel in relationships:
            rel_type = getattr(rel, "relationship_type", None)
            rel_type_str = getattr(rel_type, "name", str(rel_type))
            if rel_type_str == "IMPORTS":
                source_name = getattr(rel, "source_name", "<module>")
                target_name = getattr(rel, "target_name", "")
                
                # Register import mapping
                if target_name:
                    parts = target_name.split(".")
                    alias_name = parts[-1]
                    self.index.register_import(file_path, alias_name, target_name)

    def register_file_inheritance(self, file_path: str, relationships: List[Any]) -> None:
        """Index extends and implements relationships."""
        for rel in relationships:
            rel_type = getattr(rel, "relationship_type", None)
            rel_type_str = getattr(rel_type, "name", str(rel_type))
            if rel_type_str in ("EXTENDS", "IMPLEMENTS"):
                src = getattr(rel, "source_name", "")
                tgt = getattr(rel, "target_name", "")
                if src and tgt:
                    self.index.register_inheritance(src, tgt)

    def resolve_symbol(self, file_path: str, caller_scope: Optional[str], symbol_name: str) -> Optional[str]:
        """Resolves a referenced symbol name to its fully qualified name."""
        # 1. Try resolving relative to caller_scope (local class members/methods)
        if caller_scope:
            qname_attempt = f"{caller_scope}.{symbol_name}"
            if qname_attempt in self.index.symbol_details:
                return qname_attempt
            
            # Check if caller_scope inherits from a class and check that class for the symbol
            resolved_parent = self._check_inheritance_for_symbol(caller_scope, symbol_name)
            if resolved_parent:
                return resolved_parent

        # 2. Check if it's a local class or function defined in this file
        if symbol_name in self.index.symbol_details:
            return symbol_name

        # 3. Check if it is imported
        file_imports = self.index.file_imports.get(file_path, {})
        if symbol_name in file_imports:
            source_module, _ = file_imports[symbol_name]
            return source_module

        # 4. Global search across the repository by exact name matching
        for qname, details in self.index.symbol_details.items():
            if details["name"] == symbol_name:
                return qname

        return None

    def _check_inheritance_for_symbol(self, class_qname: str, symbol_name: str, visited: Optional[Set[str]] = None) -> Optional[str]:
        if visited is None:
            visited = set()
        if class_qname in visited:
            return None
        visited.add(class_qname)

        parents = self.index.inheritance_map.get(class_qname, set())
        for parent in parents:
            parent_attempt = f"{parent}.{symbol_name}"
            if parent_attempt in self.index.symbol_details:
                return parent_attempt
            resolved = self._check_inheritance_for_symbol(parent, symbol_name, visited)
            if resolved:
                return resolved
        return None
