class PlatformException(Exception):
    """Base exception for platform-level errors."""
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        self.code = code

class InfrastructureException(PlatformException):
    """Base exception for infrastructure errors."""
    pass

class GitOperationException(InfrastructureException):
    """Raised when a git operation fails."""
    pass

class DatabaseException(InfrastructureException):
    """Raised when a database operation fails."""
    pass
