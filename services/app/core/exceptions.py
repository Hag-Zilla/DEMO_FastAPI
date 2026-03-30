"""Custom exception classes for the application."""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, detail: str, status_code: int = 400):
        """Initialize AppException.

        Args:
            detail: Exception detail message.
            status_code: HTTP status code (default: 400).
        """
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class ValidationException(AppException):
    """Raised when validation fails."""

    def __init__(self, detail: str):
        """Initialize ValidationException."""
        super().__init__(detail, status_code=422)


class AuthenticationException(AppException):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Could not validate credentials"):
        """Initialize AuthenticationException."""
        super().__init__(detail, status_code=401)


class AuthorizationException(AppException):
    """Raised when user lacks required permissions."""

    def __init__(self, detail: str = "Not enough permissions"):
        """Initialize AuthorizationException."""
        super().__init__(detail, status_code=403)


class ResourceNotFoundException(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, detail: str):
        """Initialize ResourceNotFoundException."""
        super().__init__(detail, status_code=404)


class ConflictException(AppException):
    """Raised when a conflict occurs (e.g., duplicate resource)."""

    def __init__(self, detail: str):
        """Initialize ConflictException."""
        super().__init__(detail, status_code=409)


class InternalServerException(AppException):
    """Raised for internal server errors."""

    def __init__(self, detail: str = "Internal server error"):
        """Initialize InternalServerException."""
        super().__init__(detail, status_code=500)
