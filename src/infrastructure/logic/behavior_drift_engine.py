"""Engine for measuring behavioral drift and security boundary crossings between logic versions."""

import uuid
from datetime import datetime

from src.domain.entities.behavior_drift import BehaviorDrift
from src.domain.entities.logic_transition import LogicTransition
from src.domain.entities.logic_version import LogicVersion
from src.domain.value_objects.drift_dimensions import DriftDimensions


class BehaviorDriftEngine:
    """Computes fine-grained behavioral drift dimensions and flags security boundary crossings."""

    def compute_drift(
        self,
        transition: LogicTransition,
        version_a: LogicVersion,
        version_b: LogicVersion,
    ) -> BehaviorDrift:
        """
        Compute behavioral drift between two logic versions connected by a transition.

        Args:
            transition: The LogicTransition between the versions.
            version_a: The original LogicVersion.
            version_b: The evolved LogicVersion.

        Returns:
            A BehaviorDrift domain entity.
        """
        # 1. Compute dimensional drift scores [0.0, 1.0]
        # Structural Drift (based on structure hash equality)
        struct_drift = (
            0.0
            if version_a.fingerprint.structure_hash
            == version_b.fingerprint.structure_hash
            else 0.6
        )

        # Dependency Drift (based on calls/imports hash equality)
        dep_drift = (
            0.0
            if version_a.fingerprint.dependency_hash
            == version_b.fingerprint.dependency_hash
            else 0.7
        )

        # API Surface Drift (check if code entity identifier or location changes)
        api_drift = 0.0
        if version_a.code_entity_seid != version_b.code_entity_seid:
            api_drift = 0.5
        if version_a.metadata.get("source_file") != version_b.metadata.get(
            "source_file"
        ):
            api_drift = max(api_drift, 0.3)

        # Control Flow Drift (estimated from structural changes)
        cf_drift = 0.8 * struct_drift

        # Ontology Drift (check if parent signature's classification node changed)
        # We can extract from metadata or signature info
        ontology_changed = False
        onto_drift = 0.0
        node_a = version_a.metadata.get("ontology_node_id")
        node_b = version_b.metadata.get("ontology_node_id")
        if node_a and node_b and node_a != node_b:
            ontology_changed = True
            onto_drift = 1.0

        # Security Drift
        sec_drift = 0.0
        security_boundary_crossed = False

        # If we transition between known security nodes, e.g. from hash to direct compare
        if node_a and node_b:
            if "security" in node_a or "security" in node_b:
                if node_a != node_b:
                    security_boundary_crossed = True
                    sec_drift = 1.0

        # Even if ontology nodes are identical, check if fingerprint changes for security logic
        # e.g., bcrypt hash changed to sha256 or direct compare (reflected in dependency changes)
        if node_a and "security" in node_a:
            if dep_drift > 0.0:
                # We changed imported cryptographic libraries
                security_boundary_crossed = True
                sec_drift = 0.8

        dimension_scores = DriftDimensions(
            structural_drift=struct_drift,
            dependency_drift=dep_drift,
            api_surface_drift=api_drift,
            control_flow_drift=cf_drift,
            ontology_drift=onto_drift,
            security_drift=sec_drift,
        )

        # 2. Compute aggregate overall drift score
        overall_drift = dimension_scores.compute_overall()

        # 3. Classify category based on overall score
        category = BehaviorDrift.classify_category(overall_drift)

        return BehaviorDrift(
            id=uuid.uuid4(),
            logic_transition_id=transition.id,
            from_logic_version_id=version_a.id,
            to_logic_version_id=version_b.id,
            drift_score=overall_drift,
            drift_category=category,
            dimension_scores=dimension_scores,
            ontology_changed=ontology_changed,
            security_boundary_crossed=security_boundary_crossed,
            computed_at=datetime.utcnow(),
            metadata={},
        )
