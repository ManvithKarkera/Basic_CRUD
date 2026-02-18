"""
Custom exceptions for the application.
These exceptions are automatically handled by Flask error handlers.
"""


class APIException(Exception):
    """Base exception for all API errors."""
    status_code = 500
    message = "An error occurred"
    
    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__()
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        """Convert exception to dictionary for JSON response."""
        rv = {'error': self.message}
        if self.payload:
            rv.update(self.payload)
        return rv


class ValidationError(APIException):
    """
    Raised when input validation fails.
    Maps to HTTP 400 Bad Request.
    """
    status_code = 400
    message = "Validation error"


class NotFoundError(APIException):
    """
    Raised when a requested resource is not found.
    Maps to HTTP 404 Not Found.
    """
    status_code = 404
    message = "Resource not found"


class ConflictError(APIException):
    """
    Raised when an operation conflicts with current resource state.
    Maps to HTTP 409 Conflict.
    Examples: Invalid state transitions, modifying completed tasks.
    """
    status_code = 409
    message = "Operation conflicts with current state"
