"""Generic entity store protocol.

All identity and scoping is expressed through string-keyed filters.
Entities carry their own identity and scope fields, so save(entity)
is self-contained.

Filter values are always strings. Enum fields compare naturally
because all domain enums extend str (str, Enum).
"""

from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel, covariant=True)


@runtime_checkable
class EntityStore(Protocol[T]):
    """Generic store for domain entities.

    Single protocol replacing all entity-specific repositories.
    Scoping and identity are expressed through string-keyed filters.
    Immutability is a usecase concern, not a store concern.
    """

    def get(self, filters: dict[str, str]) -> T | None:
        """Retrieve a single entity matching all filters.

        Returns None if no match.
        """
        ...

    def search(self, filters: dict[str, str] | None = None) -> list[T]:
        """List entities matching all filters.

        None or empty filters returns all entities in the store's
        scope. Each filter is a field-name to string-value pair.
        """
        ...

    def save(self, entity: T) -> None:
        """Save an entity (create or update).

        The entity carries its own identity and scope. Save semantics
        (upsert vs append) are an implementation detail.
        """
        ...

    def delete(self, filters: dict[str, str]) -> bool:
        """Delete entity matching filters. Returns True if deleted."""
        ...
