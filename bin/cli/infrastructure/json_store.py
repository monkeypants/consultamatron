"""Generic JSON array store and low-level I/O helpers.

JsonArrayStore provides load/persist/find/upsert/append for Pydantic
models stored as JSON arrays on disk.  Repository implementations
compose with a store instance, keeping their own path resolution and
Protocol interface while delegating JSON mechanics here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def read_json_array(path: Path) -> list[dict]:
    """Read a JSON array from a file, returning [] if missing."""
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_array(path: Path, data: list[dict]) -> None:
    """Write a JSON array to a file, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def read_json_object(path: Path) -> dict | None:
    """Read a JSON object from a file, returning None if missing."""
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_object(path: Path, data: dict) -> None:
    """Write a JSON object to a file, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Generic JSON array store
# ---------------------------------------------------------------------------


class JsonArrayStore(Generic[T]):
    """Reusable load/persist/find/upsert/append for Pydantic models in a JSON array.

    Four of the six repositories share this pattern.  Each repo composes
    with a store instance, keeping its own path resolution and Protocol
    interface while delegating the JSON mechanics here.
    """

    def __init__(self, model: type[T], key_field: str) -> None:
        self._model = model
        self._key_field = key_field

    def load(self, path: Path) -> list[T]:
        return [self._model.model_validate(item) for item in read_json_array(path)]

    def persist(self, path: Path, items: list[T]) -> None:
        write_json_array(path, [item.model_dump(mode="json") for item in items])

    def find(self, items: list[T], key_value: str) -> T | None:
        for item in items:
            if getattr(item, self._key_field) == key_value:
                return item
        return None

    def upsert(self, path: Path, item: T) -> None:
        items = self.load(path)
        key_value = getattr(item, self._key_field)
        for i, existing in enumerate(items):
            if getattr(existing, self._key_field) == key_value:
                items[i] = item
                self.persist(path, items)
                return
        items.append(item)
        self.persist(path, items)

    def append(self, path: Path, item: T) -> None:
        raw = read_json_array(path)
        raw.append(item.model_dump(mode="json"))
        write_json_array(path, raw)
