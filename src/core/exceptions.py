"""
Core Exception Types.
Defines base domain exceptions that the application context layers inherit.
"""


class BasePlatformException(Exception):
    """Base exception for all system errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class DomainException(BasePlatformException):
    """Raised when business validation rules in the Domain layer are violated."""
    pass


class NotFoundException(DomainException):
    """Raised when a specific domain aggregate or entity is missing."""

    def __init__(self, entity_name: str, identifier: str):
        super().__init__(
            message=f"{entity_name} identified by {identifier} was not found.",
            code="ENTITY_NOT_FOUND",
        )


class InfrastructureException(BasePlatformException):
    """Raised when third-party software, file writing, or DB queries fail."""
    pass
