"""Generic JSON-backed EntityStore implementation.

Configurable for any Pydantic entity type stored as a JSON array.
Path resolution, key field, and save semantics are injected at
construction time.  One class replaces JsonProjectRepository,
JsonDecisionRepository, JsonEngagementLogRepository,
and JsonResearchTopicRepository.

TourManifestRepository uses JSON objects (not arrays) with directory
scanning, so it needs a separate implementation variant.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

from bin.cli.infrastructure.json_store import JsonArrayStore

T = TypeVar("T", bound=BaseModel)

PathResolver = Callable[[dict[str, str]], Path]


class JsonEntityStore(Generic[T]):
    """EntityStore backed by JSON array files.

    Constructor parameters:
        model: The Pydantic model class for deserialization.
        key_field: The entity field used as identity within a file
            (e.g. "slug" for Project, "id" for DecisionEntry).
        path_resolver: Maps a filters dict to the JSON file path.
            Only scope-relevant keys need to be present; extra keys
            are ignored by the resolver but still applied as entity
            filters.
        append_only: When True, save appends rather than upserts.
            Matches current behaviour for DecisionEntry and
            EngagementEntry.
    """

    def __init__(
        self,
        model: type[T],
        key_field: str,
        path_resolver: PathResolver,
        *,
        append_only: bool = False,
    ) -> None:
        self._store = JsonArrayStore(model, key_field)
        self._model = model
        self._key_field = key_field
        self._resolve_path = path_resolver
        self._append_only = append_only

    def get(self, filters: dict[str, str]) -> T | None:
        path = self._resolve_path(filters)
        for item in self._store.load(path):
            if _matches(item, filters):
                return item
        return None

    def search(self, filters: dict[str, str] | None = None) -> list[T]:
        filters = filters or {}
        path = self._resolve_path(filters)
        items = self._store.load(path)
        if not filters:
            return items
        return [item for item in items if _matches(item, filters)]

    def save(self, entity: T) -> None:
        scope = _string_fields(entity)
        path = self._resolve_path(scope)
        if self._append_only:
            self._store.append(path, entity)
        else:
            self._store.upsert(path, entity)

    def delete(self, filters: dict[str, str]) -> bool:
        path = self._resolve_path(filters)
        items = self._store.load(path)
        remaining = [item for item in items if not _matches(item, filters)]
        if len(remaining) == len(items):
            return False
        self._store.persist(path, remaining)
        return True


def _matches(entity: BaseModel, filters: dict[str, str]) -> bool:
    """Check whether an entity matches all filter key-value pairs.

    Comparison uses ``==`` which works for plain strings and for
    str-based enums (``ProjectStatus.PLANNING == "planning"``).
    """
    for field, value in filters.items():
        attr = getattr(entity, field, None)
        if attr is None:
            return False
        if isinstance(attr, Enum):
            if attr.value != value:
                return False
        elif attr != value:
            return False
    return True


def _string_fields(entity: BaseModel) -> dict[str, str]:
    """Extract string-valued fields from an entity for path resolution."""
    result: dict[str, str] = {}
    for field_name in type(entity).model_fields:
        val = getattr(entity, field_name)
        if isinstance(val, str):
            result[field_name] = val
    return result
