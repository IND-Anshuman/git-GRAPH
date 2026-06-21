#!/usr/bin/env python3
"""
validate_yaml_schemas.py
========================
git-GRAPH — Industrial-Grade YAML Referential Integrity Validator

Checks:
  1. All YAML files parse without syntax errors.
  2. All ontology_node_id values in pattern files resolve to real leaf nodes
     in the domain ontology files.
  3. All required_patterns / optional_patterns in concepts.yaml resolve to
     real pattern_ids in the pattern library.
  4. All capability behavior IDs in capability_registry.yaml resolve to real
     pattern_ids in the pattern library.
  5. All intent_hints in technology_decisions.yaml match IDs defined in
     strategic_intents.yaml.
  6. All framework packs that declare 'inherits' reference a valid pack id.

Usage:
    python scripts/validate_yaml_schemas.py
    python scripts/validate_yaml_schemas.py --strict  # exits 1 on warnings
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML is not installed. Run: pip install pyyaml")
    sys.exit(1)

# ───────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
ONTOLOGY_DIR = ROOT / "src" / "infrastructure" / "patterns" / "ontology"
PATTERNS_DIR = ROOT / "src" / "infrastructure" / "patterns" / "patterns"
DECISIONS_DIR = ROOT / "src" / "infrastructure" / "patterns" / "decisions"
INTENTS_DIR = ROOT / "src" / "infrastructure" / "patterns" / "intents"
FRAMEWORK_PACKS_DIR = ROOT / "data" / "framework_packs"
CAPABILITY_REGISTRY = ROOT / "data" / "capability_registry.yaml"

ONTOLOGY_SKIP = {"concepts.yaml"}  # concepts is a meta-file, not a domain ontology
# ───────────────────────────────────────────────────────────────────────


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    def error(self, msg: str) -> None:
        self.errors.append(f"  [ERROR]   {msg}")

    def warn(self, msg: str) -> None:
        self.warnings.append(f"  [WARN]    {msg}")

    def ok(self, msg: str) -> None:
        self.info.append(f"  [OK]      {msg}")

    @property
    def failed(self) -> bool:
        return len(self.errors) > 0


def load_yaml(path: Path) -> Any:
    """Load a YAML file, raising on parse errors."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def collect_leaf_node_ids(nodes: list[dict], acc: set[str] | None = None) -> set[str]:
    """Recursively collect all leaf node IDs from an ontology node list."""
    if acc is None:
        acc = set()
    for node in nodes:
        if node.get("is_leaf", False):
            acc.add(node["id"])
        children = node.get("children", [])
        if children:
            collect_leaf_node_ids(children, acc)
    return acc


def collect_all_node_ids(nodes: list[dict], acc: set[str] | None = None) -> set[str]:
    """Recursively collect ALL node IDs (leaf and non-leaf)."""
    if acc is None:
        acc = set()
    for node in nodes:
        acc.add(node["id"])
        children = node.get("children", [])
        if children:
            collect_all_node_ids(children, acc)
    return acc


# ───────────────────────────────────────────────────────────────────────
# CHECK 1 — YAML Syntax
# ───────────────────────────────────────────────────────────────────────

def check_yaml_syntax(result: ValidationResult) -> dict[Path, Any]:
    """Parse every YAML file in the project and report syntax errors."""
    parsed: dict[Path, Any] = {}
    yaml_files = list(ROOT.rglob("*.yaml")) + list(ROOT.rglob("*.yml"))
    # Skip venv and node_modules
    yaml_files = [
        f for f in yaml_files
        if ".venv" not in str(f) and "node_modules" not in str(f) and ".git" not in str(f)
    ]
    for yf in yaml_files:
        try:
            parsed[yf] = load_yaml(yf)
        except yaml.YAMLError as e:
            result.error(f"YAML syntax error in {yf.relative_to(ROOT)}: {e}")
    result.ok(f"Syntax check complete. {len(parsed)} files parsed successfully.")
    return parsed


# ───────────────────────────────────────────────────────────────────────
# CHECK 2 — Pattern ontology_node_id referential integrity
# ───────────────────────────────────────────────────────────────────────

def build_leaf_node_registry(result: ValidationResult) -> set[str]:
    """Build the set of all valid leaf ontology node IDs from domain ontology files."""
    leaf_ids: set[str] = set()
    for yf in ONTOLOGY_DIR.glob("*.yaml"):
        if yf.name in ONTOLOGY_SKIP:
            continue
        try:
            data = load_yaml(yf)
            nodes = data.get("nodes", [])
            leaf_ids.update(collect_leaf_node_ids(nodes))
        except Exception as e:
            result.error(f"Cannot load ontology file {yf.name}: {e}")
    result.ok(f"Ontology registry built: {len(leaf_ids)} leaf nodes found.")
    return leaf_ids


def check_pattern_ontology_refs(result: ValidationResult, leaf_ids: set[str]) -> set[str]:
    """Verify every pattern's ontology_node_id resolves to a known leaf node."""
    pattern_ids: set[str] = set()
    for yf in PATTERNS_DIR.glob("*.yaml"):
        try:
            data = load_yaml(yf)
            patterns = data.get("patterns", [])
            for p in patterns:
                pid = p.get("pattern_id", "<unknown>")
                pattern_ids.add(pid)
                node_id = p.get("ontology_node_id")
                if not node_id:
                    result.error(f"{yf.name} :: pattern '{pid}' missing ontology_node_id")
                elif node_id not in leaf_ids:
                    result.error(
                        f"{yf.name} :: pattern '{pid}' references unknown ontology node '{node_id}'"
                    )
        except Exception as e:
            result.error(f"Cannot load pattern file {yf.name}: {e}")
    result.ok(f"Pattern ontology check complete: {len(pattern_ids)} patterns validated.")
    return pattern_ids


# ───────────────────────────────────────────────────────────────────────
# CHECK 3 — concepts.yaml pattern references
# ───────────────────────────────────────────────────────────────────────

def check_concepts_pattern_refs(result: ValidationResult, pattern_ids: set[str]) -> None:
    """Verify required_patterns and optional_patterns in concepts.yaml exist in the pattern library."""
    concepts_file = ONTOLOGY_DIR / "concepts.yaml"
    if not concepts_file.exists():
        result.error("concepts.yaml not found at expected path.")
        return
    data = load_yaml(concepts_file)
    total_refs = 0
    missing = 0
    for domain in data.get("domains", []):
        for concept in domain.get("concepts", []):
            cid = concept.get("id", "<unknown>")
            for key in ("required_patterns", "optional_patterns"):
                for pid in concept.get(key, []):
                    total_refs += 1
                    if pid not in pattern_ids:
                        result.error(
                            f"concepts.yaml :: concept '{cid}' references unknown pattern '{pid}' in {key}"
                        )
                        missing += 1
    result.ok(f"Concepts check complete: {total_refs} pattern refs, {missing} missing.")


# ───────────────────────────────────────────────────────────────────────
# CHECK 4 — capability_registry.yaml behavior references
# ───────────────────────────────────────────────────────────────────────

def check_capability_registry_refs(result: ValidationResult, pattern_ids: set[str]) -> None:
    """Verify every behavior in capability_registry.yaml maps to a real pattern_id."""
    if not CAPABILITY_REGISTRY.exists():
        result.warn("capability_registry.yaml not found, skipping.")
        return
    data = load_yaml(CAPABILITY_REGISTRY)
    total_refs = 0
    missing = 0
    for cap_name, cap_data in data.items():
        if not isinstance(cap_data, dict):
            continue
        for behavior in cap_data.get("behaviors", []):
            total_refs += 1
            if behavior not in pattern_ids:
                result.error(
                    f"capability_registry.yaml :: capability '{cap_name}' references unknown behavior '{behavior}'"
                )
                missing += 1
    result.ok(f"Capability registry check: {total_refs} behavior refs, {missing} missing.")


# ───────────────────────────────────────────────────────────────────────
# CHECK 5 — technology_decisions.yaml intent_hints
# ───────────────────────────────────────────────────────────────────────

def check_technology_decisions_intents(result: ValidationResult) -> None:
    """Verify intent_hints in technology_decisions.yaml match IDs in strategic_intents.yaml."""
    decisions_file = DECISIONS_DIR / "technology_decisions.yaml"
    intents_file = INTENTS_DIR / "strategic_intents.yaml"
    if not decisions_file.exists() or not intents_file.exists():
        result.warn("technology_decisions.yaml or strategic_intents.yaml not found, skipping.")
        return
    intents_data = load_yaml(intents_file)
    valid_intents = {p["id"].upper() for p in intents_data.get("patterns", [])}
    decisions_data = load_yaml(decisions_file)
    total = 0
    missing = 0
    for dec in decisions_data.get("patterns", []):
        did = dec.get("id", "<unknown>")
        for hint in dec.get("intent_hints", []):
            total += 1
            if hint not in valid_intents:
                result.error(
                    f"technology_decisions.yaml :: decision '{did}' uses unknown intent_hint '{hint}'"
                )
                missing += 1
    result.ok(f"Technology decisions intent check: {total} hints, {missing} missing.")


# ───────────────────────────────────────────────────────────────────────
# CHECK 6 — Framework pack 'inherits' references
# ───────────────────────────────────────────────────────────────────────

def check_framework_pack_inheritance(result: ValidationResult) -> None:
    """Verify all 'inherits' entries in framework packs reference a valid pack file."""
    pack_files = list(FRAMEWORK_PACKS_DIR.glob("*.yaml"))
    pack_ids = {f.stem for f in pack_files}
    for yf in pack_files:
        try:
            data = load_yaml(yf)
            for parent in data.get("inherits", []):
                if parent not in pack_ids:
                    result.error(
                        f"{yf.name} :: inherits unknown pack '{parent}'"
                    )
        except Exception as e:
            result.error(f"Cannot load framework pack {yf.name}: {e}")
    result.ok(f"Framework pack inheritance check complete ({len(pack_files)} packs).")


# ───────────────────────────────────────────────────────────────────────
# MAIN
# ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="git-GRAPH YAML Referential Integrity Validator"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any warnings are found (in addition to errors).",
    )
    args = parser.parse_args()

    result = ValidationResult()

    print("\n" + "=" * 70)
    print("  git-GRAPH YAML Referential Integrity Validator")
    print("=" * 70 + "\n")

    print("[1/6] Checking YAML syntax...")
    check_yaml_syntax(result)

    print("\n[2/6] Building ontology leaf node registry...")
    leaf_ids = build_leaf_node_registry(result)

    print("\n[3/6] Validating pattern ontology_node_id references...")
    pattern_ids = check_pattern_ontology_refs(result, leaf_ids)

    print("\n[4/6] Validating concepts.yaml pattern references...")
    check_concepts_pattern_refs(result, pattern_ids)

    print("\n[5/6] Validating capability_registry.yaml behavior references...")
    check_capability_registry_refs(result, pattern_ids)

    print("\n[6/6] Validating technology decision intent_hints + framework inheritance...")
    check_technology_decisions_intents(result)

    check_framework_pack_inheritance(result)

    # ─── Summary ───
    print("\n" + "-" * 70)
    print("RESULTS:")
    for line in result.info:
        print(line)
    if result.warnings:
        print("\nWARNINGS:")
        for line in result.warnings:
            print(line)
    if result.errors:
        print("\nERRORS:")
        for line in result.errors:
            print(line)

    print("\n" + "-" * 70)
    total_issues = len(result.errors) + (len(result.warnings) if args.strict else 0)
    if total_issues == 0:
        print(f"[PASS]  All checks passed. {len(result.info)} validations OK.")
        return 0
    else:
        print(f"[FAIL]  {len(result.errors)} error(s), {len(result.warnings)} warning(s) found.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
