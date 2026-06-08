"""Registry for canonical behaviors, families, and language mappings."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BehaviorFamily:
    """Represents a category grouping multiple related canonical behaviors."""

    id: str
    name: str
    parent_concept_id: str
    description: str


@dataclass
class BehaviorMappingRule:
    """Language-specific indicators mapping to a canonical behavior."""

    language: str
    imports: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)
    heuristics: dict = field(default_factory=dict)


@dataclass
class CanonicalBehaviorDefinition:
    """Normalized action definition with language-specific rules."""

    id: str
    name: str
    family_id: str
    description: str
    mappings: List[BehaviorMappingRule] = field(default_factory=list)


class CanonicalRegistry:
    """In-memory registry for canonical behaviors and families."""

    def __init__(self) -> None:
        self._families: Dict[str, BehaviorFamily] = {}
        self._behaviors: Dict[str, CanonicalBehaviorDefinition] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        # Seed secure hashing family
        self.register_family(BehaviorFamily(
            id="secure_hashing",
            name="Secure Hashing Family",
            parent_concept_id="security.authentication",
            description="Cryptographic hash checks and validation algorithms."
        ))

        # Seed password verification behavior
        self.register_behavior(CanonicalBehaviorDefinition(
            id="auth_password_verification",
            name="Password Cryptographic Verification",
            family_id="secure_hashing",
            description="Verifies user-supplied credentials against secure cryptographic hashes.",
            mappings=[
                BehaviorMappingRule("python", ["bcrypt"], ["bcrypt.checkpw"], {}),
                BehaviorMappingRule("java", ["org.springframework.security.crypto.password.PasswordEncoder"], ["PasswordEncoder.matches"], {}),
                BehaviorMappingRule("csharp", ["Microsoft.AspNetCore.Identity.PasswordHasher"], ["PasswordHasher.VerifyHashedPassword"], {}),
                BehaviorMappingRule("rust", ["argon2"], ["argon2.verify"], {})
            ]
        ))

    def register_family(self, family: BehaviorFamily) -> None:
        """Register a new behavior family."""
        self._families[family.id] = family

    def register_behavior(self, behavior: CanonicalBehaviorDefinition) -> None:
        """Register a new canonical behavior definition."""
        self._behaviors[behavior.id] = behavior

    def get_behavior(self, behavior_id: str) -> Optional[CanonicalBehaviorDefinition]:
        """Look up a behavior by ID."""
        return self._behaviors.get(behavior_id)

    def get_family(self, family_id: str) -> Optional[BehaviorFamily]:
        """Look up a family by ID."""
        return self._families.get(family_id)

    def list_behaviors(self) -> List[CanonicalBehaviorDefinition]:
        """List all registered behaviors."""
        return list(self._behaviors.values())
