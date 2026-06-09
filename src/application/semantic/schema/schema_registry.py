"""Schema Registry service for dynamic meta-type and schema definition management."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.entities.meta_ontology import MetaType, MetaDefinition


class SchemaRegistry:
    """Manages registration, dynamic validation, and schema evolution (SemVer) of MetaTypes."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow
        # Try importing jsonschema for runtime JSON Schema validation
        try:
            import jsonschema
            self._validator_pkg = jsonschema
        except ImportError:
            self._validator_pkg = None

    def register_type(
        self,
        type_id: str,
        name: str,
        category: str,
        status: str = "EXPERIMENTAL",
    ) -> MetaType:
        """Registers a new MetaType structure identifier."""
        meta_type = MetaType(
            id=type_id,
            name=name,
            category=category,
            status=status,
            created_at=datetime.utcnow(),
        )
        meta_type.validate()

        with self.uow:
            existing = self.uow.meta_types.get_by_id(type_id)
            if existing:
                # If exists, update details
                existing.name = name
                existing.category = category
                existing.status = status
                self.uow.meta_types.save(existing)
                meta_type = existing
            else:
                self.uow.meta_types.save(meta_type)
            self.uow.commit()

        return meta_type

    def register_definition(
        self,
        type_id: str,
        schema_definition: Dict[str, Any],
        semantic_signature: Dict[str, Any],
        version_string: str = "1.0.0",
    ) -> MetaDefinition:
        """Registers a new versioned schema schema configuration for a MetaType."""
        major, minor, patch = self.parse_version(version_string)

        with self.uow:
            meta_type = self.uow.meta_types.get_by_id(type_id)
            if not meta_type:
                raise ValueError(f"MetaType '{type_id}' is not registered.")

            # Validate the schema itself if jsonschema is available
            if self._validator_pkg:
                try:
                    self._validator_pkg.Draft7Validator.check_schema(schema_definition)
                except Exception as e:
                    raise ValueError(f"Invalid JSON Schema definition: {e}")

            # Check if this exact version already exists
            existing = self.uow.meta_definitions.get_by_version(type_id, major, minor, patch)
            if existing:
                raise ValueError(f"MetaDefinition version {version_string} for '{type_id}' already exists.")

            meta_def = MetaDefinition(
                id=uuid.uuid4(),
                type_id=type_id,
                major_version=major,
                minor_version=minor,
                patch_version=patch,
                schema_definition=schema_definition,
                semantic_signature=semantic_signature,
                created_at=datetime.utcnow(),
            )
            meta_def.validate()
            self.uow.meta_definitions.save(meta_def)
            self.uow.commit()

        return meta_def

    def validate_instance(self, type_id: str, instance_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validates an instance dictionary against the latest schema of the target MetaType."""
        with self.uow:
            latest_def = self.uow.meta_definitions.get_latest_definition(type_id)
            if not latest_def:
                return False, f"No schema definitions registered for type '{type_id}'."

            schema = latest_def.schema_definition

            # Validation logic
            if self._validator_pkg:
                try:
                    self._validator_pkg.validate(instance=instance_data, schema=schema)
                    return True, None
                except self._validator_pkg.ValidationError as e:
                    return False, str(e)
            else:
                # Basic fallback key matching: ensure required properties are present
                required_keys = schema.get("required", [])
                for key in required_keys:
                    if key not in instance_data:
                        return False, f"Missing required property: '{key}'"
                
                # Check types if specified in properties
                properties = schema.get("properties", {})
                for key, val in instance_data.items():
                    if key in properties:
                        expected_type = properties[key].get("type")
                        if expected_type == "string" and not isinstance(val, str):
                            return False, f"Property '{key}' must be string, got {type(val).__name__}"
                        elif expected_type == "integer" and not isinstance(val, int):
                            return False, f"Property '{key}' must be integer, got {type(val).__name__}"
                        elif expected_type == "number" and not isinstance(val, (int, float)):
                            return False, f"Property '{key}' must be number, got {type(val).__name__}"
                        elif expected_type == "boolean" and not isinstance(val, bool):
                            return False, f"Property '{key}' must be boolean, got {type(val).__name__}"
                        elif expected_type == "array" and not isinstance(val, list):
                            return False, f"Property '{key}' must be array, got {type(val).__name__}"
                        elif expected_type == "object" and not isinstance(val, dict):
                            return False, f"Property '{key}' must be object, got {type(val).__name__}"

                return True, None

    @staticmethod
    def parse_version(version_string: str) -> Tuple[int, int, int]:
        """Parses a SemVer string into major, minor, patch tuple."""
        try:
            parts = version_string.split(".")
            if len(parts) != 3:
                raise ValueError()
            return int(parts[0]), int(parts[1]), int(parts[2])
        except Exception:
            raise ValueError(f"Invalid SemVer string format: '{version_string}'. Expected 'major.minor.patch'.")
