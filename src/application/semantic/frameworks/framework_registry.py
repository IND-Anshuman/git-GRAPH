"""Framework Registry for mapping annotations/decorators to semantic roles."""

from typing import Dict, Optional


class FrameworkRegistry:
    """Holds decorator mapping and metadata lookup rules for popular frameworks."""

    def __init__(self) -> None:
        # Maps decorators/annotations to Canonical Entity Roles
        self._entity_mappings: Dict[str, str] = {
            # Python
            "@app.get": "APIEndpoint",
            "@app.post": "APIEndpoint",
            # Java
            "@RestController": "Controller",
            "@Service": "Service",
            "@Repository": "Repository",
            "@GetMapping": "APIEndpoint",
            "@PostMapping": "APIEndpoint",
            # TypeScript
            "@Controller": "Controller",
            "@Injectable": "Service",
            "@Get": "APIEndpoint",
            "@Post": "APIEndpoint",
            # C#
            "[ApiController]": "Controller",
            "[HttpGet]": "APIEndpoint",
            "[HttpPost]": "APIEndpoint",
        }

        # Maps decorators/annotations to Relationship types
        self._relationship_mappings: Dict[str, str] = {
            "@Autowired": "INJECTS",
            "[Inject]": "INJECTS",
            "Depends": "INJECTS",
        }

    def get_role_for_decorator(self, decorator: str) -> Optional[str]:
        """
        Resolves entity role from a framework decorator/annotation.
        
        Args:
            decorator: Extracted annotation string.
            
        Returns:
            Optional structural role mapping (e.g. Controller, APIEndpoint).
        """
        for dec, role in self._entity_mappings.items():
            if decorator.startswith(dec):
                return role
        return None

    def get_relationship_for_decorator(self, decorator: str) -> Optional[str]:
        """
        Resolves relationship type from a framework decorator/annotation.
        
        Args:
            decorator: Extracted annotation string.
            
        Returns:
            Optional relationship mapping string (e.g. INJECTS).
        """
        for dec, rel in self._relationship_mappings.items():
            if decorator.startswith(dec):
                return rel
        return None
