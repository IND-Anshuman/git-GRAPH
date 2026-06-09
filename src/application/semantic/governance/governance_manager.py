"""Governance Manager service to coordinate MetaType lifecycle promotion and validation."""

from datetime import datetime
from typing import Tuple
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.entities.meta_ontology import MetaType


class GovernanceManager:
    """Coordinates Promotion Workflows (Experimental -> Candidate -> Active -> Deprecated).

    Enforces threshold checks, metadata validation, and human-in-the-loop approvals.
    """

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    def request_promotion_to_candidate(self, type_id: str) -> Tuple[bool, str]:
        """Validates thresholds to promote a MetaType from EXPERIMENTAL to CANDIDATE."""
        with self.uow:
            meta_type = self.uow.meta_types.get_by_id(type_id)
            if not meta_type:
                return False, f"MetaType '{type_id}' not found."

            if meta_type.status != "EXPERIMENTAL":
                return False, f"MetaType status is '{meta_type.status}'; cannot promote to CANDIDATE."

            # Check: Must have at least one schema definition registered
            latest_def = self.uow.meta_definitions.get_latest_definition(type_id)
            if not latest_def:
                return False, "Promotion failed: MetaType has no schema definitions."

            # Check: Check if schema definition is substantial (e.g. has fields)
            schema = latest_def.schema_definition
            if not schema or not schema.get("properties"):
                return False, "Promotion failed: Schema definition properties are empty."

            # Eligible! Perform state transition
            meta_type.status = "CANDIDATE"
            self.uow.meta_types.save(meta_type)
            self.uow.commit()

        return True, "Successfully promoted MetaType to CANDIDATE."

    def approve_promotion_to_active(self, type_id: str, approver_name: str) -> Tuple[bool, str]:
        """Admin/Human-in-the-loop approval to transition MetaType from CANDIDATE to ACTIVE."""
        if not approver_name:
            return False, "An approver name must be specified for human-in-the-loop promotion."

        with self.uow:
            meta_type = self.uow.meta_types.get_by_id(type_id)
            if not meta_type:
                return False, f"MetaType '{type_id}' not found."

            if meta_type.status != "CANDIDATE":
                return False, f"MetaType status is '{meta_type.status}'; only CANDIDATE types can be promoted to ACTIVE."

            # Transition state
            meta_type.status = "ACTIVE"
            self.uow.meta_types.save(meta_type)
            self.uow.commit()

        return True, f"MetaType '{type_id}' approved as ACTIVE by {approver_name}."

    def deprecate_type(self, type_id: str) -> Tuple[bool, str]:
        """Transitions a MetaType status to DEPRECATED."""
        with self.uow:
            meta_type = self.uow.meta_types.get_by_id(type_id)
            if not meta_type:
                return False, f"MetaType '{type_id}' not found."

            meta_type.status = "DEPRECATED"
            self.uow.meta_types.save(meta_type)
            self.uow.commit()

        return True, f"MetaType '{type_id}' has been deprecated."
