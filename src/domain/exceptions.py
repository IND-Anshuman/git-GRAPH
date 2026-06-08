class DomainException(Exception):
    """Base exception for all domain layer errors."""
    pass

class EntityNotFoundException(DomainException):
    """Raised when an entity is not found."""
    pass

class DuplicateEntityException(DomainException):
    """Raised when attempting to create an entity that already exists."""
    pass

class InvalidEntityException(DomainException):
    """Raised when an entity fails validation."""
    pass

class RepositoryNotFoundException(DomainException):
    """Raised when a repository is not found."""
    pass

class ParsingException(DomainException):
    """Raised when source code parsing fails."""
    pass

class ExtractionException(DomainException):
    """Raised when entity extraction fails."""
    pass


class LogicExtractionException(DomainException):
    """Raised when logic extraction fails for an entity."""

    pass


class OntologyLoadException(DomainException):
    """Raised when ontology YAML files fail to load or validate."""

    pass


class ConceptDomainException(DomainException):
    """Base exception for all Concept Graph domain issues."""

    pass


class ConceptNotFoundException(ConceptDomainException):
    """Raised when the requested Concept UUID is not registered in the database."""

    pass


class ConceptOntologyViolationException(ConceptDomainException):
    """Raised when concept detection rules violate ontology validation invariants."""

    pass

