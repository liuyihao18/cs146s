"""
Custom exceptions for the application.
"""

from __future__ import annotations


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        self.message = message
        self.error_code = error_code or "INTERNAL_ERROR"
        super().__init__(self.message)


class ValidationError(AppException):
    """Validation error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "VALIDATION_ERROR")


class NotFoundError(AppException):
    """Resource not found error."""

    def __init__(self, resource: str, resource_id: int) -> None:
        super().__init__(
            f"{resource} with id {resource_id} not found",
            "NOT_FOUND",
        )


class DatabaseError(AppException):
    """Database operation error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "DATABASE_ERROR")


class LLMError(AppException):
    """LLM operation error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "LLM_ERROR")
