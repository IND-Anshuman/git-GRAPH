"""Engine that computes detailed diffs between logic versions."""

from typing import Any, Dict

from src.domain.entities.logic_version import LogicVersion


class LogicDiffEngine:
    """Computes structural, dependency, and confidence diffs between two LogicVersions."""

    def diff_versions(
        self, version_a: LogicVersion, version_b: LogicVersion
    ) -> Dict[str, Any]:
        """
        Compute differences between two LogicVersion entities.

        Returns:
            A dictionary containing boolean flags for changes in each dimension,
            the confidence drift, and a text summary.
        """
        struct_changed = (
            version_a.fingerprint.structure_hash
            != version_b.fingerprint.structure_hash
        )
        dep_changed = (
            version_a.fingerprint.dependency_hash
            != version_b.fingerprint.dependency_hash
        )
        beh_changed = (
            version_a.fingerprint.behavioral_hash
            != version_b.fingerprint.behavioral_hash
        )

        has_changes = struct_changed or dep_changed or beh_changed
        confidence_drift = version_b.overall_confidence - version_a.overall_confidence

        # Generate a descriptive summary
        changes = []
        if struct_changed:
            changes.append("structural (AST shape)")
        if dep_changed:
            changes.append("dependencies (imports or calls)")
        if beh_changed:
            changes.append("behavioral (data flows or keywords)")

        if not has_changes:
            summary = "No behavioral changes detected."
        else:
            summary = f"Detected changes in: {', '.join(changes)}."
            if abs(confidence_drift) > 0.01:
                direction = "increased" if confidence_drift > 0 else "decreased"
                summary += f" Detection confidence {direction} by {abs(confidence_drift):.2f}."

        return {
            "has_changes": has_changes,
            "structural_changed": struct_changed,
            "dependency_changed": dep_changed,
            "behavioral_changed": beh_changed,
            "confidence_drift": confidence_drift,
            "summary": summary,
            "metadata_diff": {
                "from_file": version_a.metadata.get("source_file"),
                "to_file": version_b.metadata.get("source_file"),
            },
        }
