import os
import yaml
from pathlib import Path
from src.infrastructure.extraction.compiler.compiler_context import CompilerContext
from src.infrastructure.extraction.registries.framework_pack_registry import FrameworkPackRegistry
from src.infrastructure.extraction.compiler.passes.base import ICompilerPass

class Pass2FrameworkResolution(ICompilerPass):
    """Pass 2: Framework Resolution. Scans imports and decorators to identify active framework packs."""
    
    def __init__(self, registry: FrameworkPackRegistry | None = None):
        self.registry = registry or FrameworkPackRegistry()

    def execute(self, context: CompilerContext) -> None:
        pack_names = []
        if self.registry.data_dir.exists():
            for f in os.listdir(self.registry.data_dir):
                if f.endswith(".yaml") and f != "web_framework.yaml":
                    pack_names.append(f[:-5])
        
        for name in pack_names:
            pack = self.registry.get_pack(name)
            
            # Heuristic 1: Imports check
            framework_imported = False
            for imp in context.imports:
                imp_lower = imp.lower()
                if name in imp_lower or imp_lower.startswith(name):
                    framework_imported = True
                    break
            
            # Heuristic 2: Decorators / entity name matching in code
            code_has_framework_signatures = False
            for entity in context.raw_entities:
                # Check entity name or class heritage
                if entity.name in pack.get("entities", {}):
                    code_has_framework_signatures = True
                    break
                # Check raw decorators if any
                decorators = entity.metadata.get("decorators", [])
                for dec in decorators:
                    if dec in pack.get("decorators", {}):
                        code_has_framework_signatures = True
                        break
            
            # Heuristic 3: Check source code substring (fallback for weak signals)
            if not framework_imported and not code_has_framework_signatures:
                if f"import {name}" in context.source_code or f"from {name}" in context.source_code:
                    framework_imported = True
            
            if framework_imported or code_has_framework_signatures:
                if name not in context.frameworks_detected:
                    context.frameworks_detected.append(name)
                    
        # Resolve all inherited packs
        resolved_all = []
        for f in context.frameworks_detected:
            if f not in resolved_all:
                resolved_all.append(f)
            pack_path = self.registry.data_dir / f"{f}.yaml"
            if pack_path.exists():
                with open(pack_path, "r", encoding="utf-8") as file:
                    raw_data = yaml.safe_load(file) or {}
                    for parent in raw_data.get("inherits", []):
                        if parent not in resolved_all:
                            resolved_all.append(parent)
                            
        context.frameworks_detected = resolved_all
