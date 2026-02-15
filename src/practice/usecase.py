"""Usecase protocol.

Every usecase takes a typed request and returns a typed response.
This is the contract that all bounded context usecases satisfy.
"""

from __future__ import annotations

from typing import Protocol, TypeVar

TRequest = TypeVar("TRequest", contravariant=True)
TResponse = TypeVar("TResponse", covariant=True)


class UseCase(Protocol[TRequest, TResponse]):
    """Contract: every usecase takes a typed request, returns a typed response."""

    def execute(self, request: TRequest) -> TResponse: ...
