"""Domain exceptions for consulting practice operations."""


class DomainError(Exception):
    """Base for all domain-level errors raised by usecases."""


class NotFoundError(DomainError):
    """A required entity does not exist."""


class DuplicateError(DomainError):
    """An entity with the same identity already exists."""


class InvalidTransitionError(DomainError):
    """A requested state transition violates domain rules."""
