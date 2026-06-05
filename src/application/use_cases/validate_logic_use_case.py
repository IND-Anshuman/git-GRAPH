"""Use case for validating logic, signatures, and transition integrity."""

from dataclasses import dataclass, field
from typing import Callable, List

from src.application.ports.unit_of_work import IUnitOfWork


@dataclass
class ValidationIssue:
    """Represents a logic integrity violation."""

    issue_type: str
    severity: str
    description: str
    target_id: str


@dataclass
class LogicValidationReport:
    """Consolidated report of logic validation checks."""

    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)


class ValidateLogicUseCase:
    """Runs integrity checks across signatures, versions, and transitions to ensure temporal graph consistency."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(self) -> LogicValidationReport:
        """Run validation rules and return a validation report."""
        issues: List[ValidationIssue] = []

        with self.uow_factory() as uow:
            # 1. Fetch all nodes, signatures, versions, and transitions
            all_nodes = {n.id: n for n in uow.ontology_nodes.list_all()}

            repositories = uow.repositories.list_all()

            for repo in repositories:
                repo_sigs = uow.logic_signatures.list_by_repository(repo.id)
                for sig in repo_sigs:
                    # Check ontology node references
                    if (
                        sig.ontology_node_id
                        and sig.ontology_node_id not in all_nodes
                    ):
                        issues.append(
                            ValidationIssue(
                                issue_type="ORPHAN_ONTOLOGY_REFERENCE",
                                severity="ERROR",
                                description=f"Signature reference to ontology node '{sig.ontology_node_id}' is not loaded.",
                                target_id=str(sig.id),
                            )
                        )

                    # Check versions under this signature
                    versions = uow.logic_versions.list_by_signature(sig.id)
                    if not versions:
                        issues.append(
                            ValidationIssue(
                                issue_type="SIGNATURE_WITHOUT_VERSIONS",
                                severity="WARNING",
                                description=f"Logic signature '{sig.canonical_name}' has no registered logic versions.",
                                target_id=str(sig.id),
                            )
                        )

                    for v in versions:
                        # Check FK to signature
                        if v.logic_signature_id != sig.id:
                            issues.append(
                                ValidationIssue(
                                    issue_type="MISMATCHED_PARENT_SIGNATURE",
                                    severity="ERROR",
                                    description=f"Version has parent signature ID '{v.logic_signature_id}' but retrieved via signature ID '{sig.id}'.",
                                    target_id=str(v.id),
                                )
                            )

                        # Check confidence score bounds
                        if not (0.0 <= v.overall_confidence <= 1.0):
                            issues.append(
                                ValidationIssue(
                                    issue_type="INVALID_CONFIDENCE_SCORE",
                                    severity="ERROR",
                                    description=f"Confidence score {v.overall_confidence} is out of bounds [0.0, 1.0].",
                                    target_id=str(v.id),
                                )
                            )

                    # Check transitions under this signature
                    transitions = uow.logic_transitions.list_by_signature(sig.id)
                    for t in transitions:
                        # Check from/to version references
                        to_ver = uow.logic_versions.get_by_id(
                            t.to_logic_version_id
                        )
                        if not to_ver:
                            issues.append(
                                ValidationIssue(
                                    issue_type="ORPHAN_TRANSITION_TARGET",
                                    severity="ERROR",
                                    description=f"Transition targets non-existent version ID '{t.to_logic_version_id}'.",
                                    target_id=str(t.id),
                                )
                            )

                        if t.from_logic_version_id:
                            from_ver = uow.logic_versions.get_by_id(
                                t.from_logic_version_id
                            )
                            if not from_ver:
                                issues.append(
                                    ValidationIssue(
                                        issue_type="ORPHAN_TRANSITION_SOURCE",
                                        severity="ERROR",
                                        description=f"Transition originates from non-existent version ID '{t.from_logic_version_id}'.",
                                        target_id=str(t.id),
                                    )
                                )

                            # Check for loop
                            if t.from_logic_version_id == t.to_logic_version_id:
                                issues.append(
                                    ValidationIssue(
                                        issue_type="SELF_LOOP_TRANSITION",
                                        severity="ERROR",
                                        description="Transition loops back to the same logic version.",
                                        target_id=str(t.id),
                                    )
                                )

        is_valid = not any(i.severity == "ERROR" for i in issues)
        return LogicValidationReport(is_valid=is_valid, issues=issues)
