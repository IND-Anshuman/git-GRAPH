"""Service for computing LogicFingerprints from ASTFeatures."""

import hashlib

from src.application.ports.ast_feature_port import ASTFeatures
from src.domain.value_objects.logic_fingerprint import LogicFingerprint


class LogicFingerprintEngine:
    """Computes deterministic LogicFingerprint from extracted AST features."""

    def compute_fingerprint(self, features: ASTFeatures) -> LogicFingerprint:
        """
        Compute a three-dimensional logic fingerprint from AST features.

        Args:
            features: The extracted ASTFeatures collection.

        Returns:
            A new LogicFingerprint containing structural, dependency, behavioral,
            and composite hashes.
        """
        # 1. Compute Structure Hash (decorators, comparisons, subscripts)
        struct_elements = []
        for d in features.decorators:
            struct_elements.append(f"dec:{d.symbol}")
        for c in features.comparisons:
            struct_elements.append(f"comp:{c.symbol}")
        for s in features.subscripts:
            struct_elements.append(f"sub:{s.symbol}")
        # Sort for determinism
        struct_str = ",".join(sorted(struct_elements))
        structure_hash = hashlib.sha256(struct_str.encode("utf-8")).hexdigest()

        # 2. Compute Dependency Hash (imports, calls)
        dep_elements = []
        for imp in features.imports:
            dep_elements.append(f"imp:{imp.symbol}")
        for call in features.calls:
            dep_elements.append(f"call:{call.symbol}")
        dep_str = ",".join(sorted(dep_elements))
        dependency_hash = hashlib.sha256(dep_str.encode("utf-8")).hexdigest()

        # 3. Compute Behavioral Hash (data flows, strings)
        beh_elements = []
        for s in features.strings:
            beh_elements.append(f"str:{s.symbol}")
        for flow in features.data_flows:
            beh_elements.append(
                f"flow:{flow.get('source')}->{flow.get('sink')}"
            )
        beh_str = ",".join(sorted(beh_elements))
        behavioral_hash = hashlib.sha256(beh_str.encode("utf-8")).hexdigest()

        # 4. Return the computed value object
        return LogicFingerprint.compute(
            structure_hash=structure_hash,
            dependency_hash=dependency_hash,
            behavioral_hash=behavioral_hash,
        )
