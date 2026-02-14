"""JSON file-backed repository implementations.

Each implementation takes a root path in its constructor and
derives file locations following the workspace conventions
defined in config.py. The directory structure carries semantic
meaning — the client ID is the directory name, not a field in
a file.

    {workspace_root}/
    └── {client}/
        ├── index.json
        ├── engagement.json
        ├── resources/
        │   └── index.json
        └── projects/
            ├── index.json
            └── {project-slug}/
                ├── decisions.json
                └── presentations/
                    └── {tour-name}/
                        └── manifest.json

    {skillsets_root}/
    └── index.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

from bin.cli.entities import (
    DecisionEntry,
    EngagementEntry,
    Project,
    ProjectStatus,
    ResearchTopic,
    Skillset,
    TourManifest,
)

T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# Shared I/O helpers
# ---------------------------------------------------------------------------


def _read_json_array(path: Path) -> list[dict]:
    """Read a JSON array from a file, returning [] if missing."""
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json_array(path: Path, data: list[dict]) -> None:
    """Write a JSON array to a file, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _read_json_object(path: Path) -> dict | None:
    """Read a JSON object from a file, returning None if missing."""
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json_object(path: Path, data: dict) -> None:
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
        return [self._model.model_validate(item) for item in _read_json_array(path)]

    def persist(self, path: Path, items: list[T]) -> None:
        _write_json_array(path, [item.model_dump(mode="json") for item in items])

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
        raw = _read_json_array(path)
        raw.append(item.model_dump(mode="json"))
        _write_json_array(path, raw)


# ---------------------------------------------------------------------------
# Skillset
# ---------------------------------------------------------------------------


class JsonSkillsetRepository:
    """Read-only skillset repository backed by a single JSON file."""

    def __init__(self, skillsets_root: Path) -> None:
        self._store: JsonArrayStore[Skillset] = JsonArrayStore(Skillset, "name")
        self._file = skillsets_root / "index.json"

    def get(self, name: str) -> Skillset | None:
        return self._store.find(self._store.load(self._file), name)

    def list_all(self) -> list[Skillset]:
        return self._store.load(self._file)


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


class JsonProjectRepository:
    """Project repository. One index.json per client under projects/."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root
        self._store: JsonArrayStore[Project] = JsonArrayStore(Project, "slug")

    def _file(self, client: str) -> Path:
        return self._root / client / "projects" / "index.json"

    def get(self, client: str, slug: str) -> Project | None:
        return self._store.find(self._store.load(self._file(client)), slug)

    def list_all(self, client: str) -> list[Project]:
        return self._store.load(self._file(client))

    def list_filtered(
        self,
        client: str,
        skillset: str | None = None,
        status: ProjectStatus | None = None,
    ) -> list[Project]:
        projects = self._store.load(self._file(client))
        if skillset is not None:
            projects = [p for p in projects if p.skillset == skillset]
        if status is not None:
            projects = [p for p in projects if p.status == status]
        return projects

    def save(self, project: Project) -> None:
        self._store.upsert(self._file(project.client), project)

    def delete(self, client: str, slug: str) -> bool:
        path = self._file(client)
        items = self._store.load(path)
        filtered = [p for p in items if p.slug != slug]
        if len(filtered) == len(items):
            return False
        self._store.persist(path, filtered)
        return True

    def client_exists(self, client: str) -> bool:
        return (self._root / client).is_dir()


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------


class JsonDecisionRepository:
    """Append-only decision repository. One file per project."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root
        self._store: JsonArrayStore[DecisionEntry] = JsonArrayStore(DecisionEntry, "id")

    def _file(self, client: str, project_slug: str) -> Path:
        return self._root / client / "projects" / project_slug / "decisions.json"

    def get(self, client: str, project_slug: str, id: str) -> DecisionEntry | None:
        return self._store.find(self._store.load(self._file(client, project_slug)), id)

    def list_all(self, client: str, project_slug: str) -> list[DecisionEntry]:
        return self._store.load(self._file(client, project_slug))

    def list_filtered(
        self,
        client: str,
        project_slug: str,
        title: str | None = None,
    ) -> list[DecisionEntry]:
        entries = self._store.load(self._file(client, project_slug))
        if title is not None:
            entries = [e for e in entries if e.title == title]
        return entries

    def save(self, entry: DecisionEntry) -> None:
        self._store.append(self._file(entry.client, entry.project_slug), entry)


# ---------------------------------------------------------------------------
# Engagement
# ---------------------------------------------------------------------------


class JsonEngagementRepository:
    """Append-only engagement repository. One file per client."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root
        self._store: JsonArrayStore[EngagementEntry] = JsonArrayStore(
            EngagementEntry, "id"
        )

    def _file(self, client: str) -> Path:
        return self._root / client / "engagement.json"

    def get(self, client: str, id: str) -> EngagementEntry | None:
        return self._store.find(self._store.load(self._file(client)), id)

    def list_all(self, client: str) -> list[EngagementEntry]:
        return self._store.load(self._file(client))

    def save(self, entry: EngagementEntry) -> None:
        self._store.append(self._file(entry.client), entry)


# ---------------------------------------------------------------------------
# Research topic
# ---------------------------------------------------------------------------


class JsonResearchTopicRepository:
    """Research topic repository. One index.json per client under resources/."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root
        self._store: JsonArrayStore[ResearchTopic] = JsonArrayStore(
            ResearchTopic, "filename"
        )

    def _file(self, client: str) -> Path:
        return self._root / client / "resources" / "index.json"

    def get(self, client: str, filename: str) -> ResearchTopic | None:
        return self._store.find(self._store.load(self._file(client)), filename)

    def list_all(self, client: str) -> list[ResearchTopic]:
        return self._store.load(self._file(client))

    def save(self, topic: ResearchTopic) -> None:
        self._store.upsert(self._file(topic.client), topic)

    def exists(self, client: str, filename: str) -> bool:
        return self.get(client, filename) is not None


# ---------------------------------------------------------------------------
# Tour manifest
# ---------------------------------------------------------------------------


class JsonTourManifestRepository:
    """Tour manifest repository. One manifest.json per tour directory."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root

    def _file(self, client: str, project_slug: str, tour_name: str) -> Path:
        return (
            self._root
            / client
            / "projects"
            / project_slug
            / "presentations"
            / tour_name
            / "manifest.json"
        )

    def get(
        self, client: str, project_slug: str, tour_name: str
    ) -> TourManifest | None:
        data = _read_json_object(self._file(client, project_slug, tour_name))
        if data is None:
            return None
        return TourManifest.model_validate(data)

    def list_all(self, client: str, project_slug: str) -> list[TourManifest]:
        """List all tour manifests for a project."""
        pres_dir = self._root / client / "projects" / project_slug / "presentations"
        if not pres_dir.is_dir():
            return []
        manifests = []
        for tour_dir in sorted(pres_dir.iterdir()):
            if not tour_dir.is_dir():
                continue
            data = _read_json_object(tour_dir / "manifest.json")
            if data is not None:
                manifests.append(TourManifest.model_validate(data))
        return manifests

    def save(self, manifest: TourManifest) -> None:
        _write_json_object(
            self._file(manifest.client, manifest.project_slug, manifest.name),
            manifest.model_dump(mode="json"),
        )
