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
