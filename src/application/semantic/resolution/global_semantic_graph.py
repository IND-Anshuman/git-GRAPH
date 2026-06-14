"""Global Semantic Graph for repository-wide symbol tracking."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set

@dataclass
class CanonicalSymbol:
    qualified_name: str
    entity_type: str  # 'CLASS', 'FUNCTION', 'METHOD', 'MODULE', 'PACKAGE', 'EXTERNAL'
    file_path: str
    scope_id: str
    aliases: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GlobalSemanticGraph:
    """Repository-wide graph of symbols, imports, and variables."""
    # Qualified name -> CanonicalSymbol
    symbols: Dict[str, CanonicalSymbol] = field(default_factory=dict)
    # File path -> dict of local alias -> target canonical/qualified name or import source
    aliases: Dict[str, Dict[str, str]] = field(default_factory=dict)
    # File path -> list of raw import dicts
    # Each import dict has: module_name, symbol_name (e.g. verify_password), alias (optional)
    imports: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    # External package/service dependencies (name -> metadata)
    external_dependencies: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Variable types: file_path -> variable_name -> type_name (e.g. OrderRepository)
    type_bindings: Dict[str, Dict[str, str]] = field(default_factory=dict)
    # Caller qualified name -> list of callee qualified names
    call_graph: Dict[str, List[str]] = field(default_factory=dict)

    def add_call(self, caller: str, callee: str) -> None:
        """Register a call relationship in the global call graph."""
        if caller not in self.call_graph:
            self.call_graph[caller] = []
        if callee not in self.call_graph[caller]:
            self.call_graph[caller].append(callee)

    def add_symbol(self, symbol: CanonicalSymbol) -> None:
        """Register a canonical symbol in the repository."""
        self.symbols[symbol.qualified_name] = symbol
        if symbol.qualified_name not in symbol.aliases:
            symbol.aliases.append(symbol.qualified_name)

    def add_alias(self, file_path: str, alias: str, target: str) -> None:
        """Register a local alias/variable assignment in a file."""
        if file_path not in self.aliases:
            self.aliases[file_path] = {}
        self.aliases[file_path][alias] = target

    def add_import(self, file_path: str, module_name: str, symbol_name: Optional[str] = None, alias: Optional[str] = None) -> None:
        """Register an import statement in a file."""
        if file_path not in self.imports:
            self.imports[file_path] = []
        self.imports[file_path].append({
            "module_name": module_name,
            "symbol_name": symbol_name,
            "alias": alias
        })

    def add_external_dependency(self, name: str, dep_type: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register an external dependency package/service/model stub."""
        self.external_dependencies[name] = {
            "name": name,
            "type": dep_type,
            "metadata": metadata or {}
        }

    def bind_type(self, file_path: str, var_name: str, type_name: str) -> None:
        """Bind a variable to an inferred type in a file."""
        if file_path not in self.type_bindings:
            self.type_bindings[file_path] = {}
        self.type_bindings[file_path][var_name] = type_name

    def resolve_symbol(self, file_path: str, local_name: str, scope_id: Optional[str] = None) -> Optional[str]:
        """Resolves a local symbol reference within a file to its canonical qualified name.
        
        Supports resolving:
          - Direct imported symbols (e.g. from utils.auth import verify_password -> utils.auth.verify_password)
          - Aliased imports (e.g. import redis as r; r.get -> redis.get or redis.Redis.get)
          - Member calls (e.g. self.repo.save -> OrderRepository.save -> repositories.order.OrderRepository.save)
          - Instantiated variables (e.g. repo.save -> OrderRepository.save)
        """
        # Clean local_name (strip self. or this.)
        clean_name = local_name
        is_self_attr = False
        if clean_name.startswith("self."):
            clean_name = clean_name[5:]
            is_self_attr = True
        elif clean_name.startswith("this."):
            clean_name = clean_name[5:]
            is_self_attr = True

        parts = clean_name.split(".")
        base_name = parts[0]

        # 1. Check local variable/alias bindings
        resolved_base = base_name
        local_aliases = self.aliases.get(file_path, {})
        
        # Follow alias chain
        visited = set()
        while resolved_base in local_aliases and resolved_base not in visited:
            visited.add(resolved_base)
            resolved_base = local_aliases[resolved_base]

        # 2. Check type bindings
        var_types = self.type_bindings.get(file_path, {})
        resolved_type = var_types.get(resolved_base, resolved_base)

        # 3. Check imports
        file_imports = self.imports.get(file_path, [])
        imported_module = None
        imported_symbol = None

        for imp in file_imports:
            # Check symbol imports first (e.g. from utils.auth import PasswordHasher)
            if imp["symbol_name"]:
                if imp["alias"] == resolved_type or imp["symbol_name"] == resolved_type:
                    imported_module = imp["module_name"]
                    imported_symbol = imp["symbol_name"]
                    break
            # Check module imports (e.g. import redis as r or import redis)
            else:
                if imp["alias"] == resolved_type or imp["module_name"] == resolved_type:
                    imported_module = imp["module_name"]
                    break

        # Reconstruct canonical path
        if imported_module:
            if imported_symbol:
                canonical_path = f"{imported_module}.{imported_symbol}"
            else:
                canonical_path = imported_module
            # Append remaining attribute parts
            if len(parts) > 1:
                canonical_path = f"{canonical_path}.{'.'.join(parts[1:])}"
        else:
            # If not imported, check if it's a known canonical symbol directly or module-prefixed
            canonical_path = clean_name
            # Try matching package/module context
            module_prefix = file_path.replace("/", ".").replace("\\", ".").replace(".py", "").replace(".ts", "").replace(".js", "")
            possible_qname = f"{module_prefix}.{clean_name}"
            if possible_qname in self.symbols:
                return possible_qname

        # 4. Resolve type inheritance / members if it maps to a class method
        # e.g., if canonical_path is redis.get, and redis.Redis.get exists, resolve to that.
        # Check direct canonical match
        if canonical_path in self.symbols:
            return canonical_path

        # Try appending to matching imports
        # E.g. utils.auth.verify_password
        for qname in self.symbols:
            if qname.endswith(canonical_path):
                return qname

        return canonical_path
