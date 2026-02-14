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

from bin.cli.entities import (
    DecisionEntry,
    EngagementEntry,
    Project,
    ProjectStatus,
    ResearchTopic,
    Skillset,
    TourManifest,
)


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
# Skillset
# ---------------------------------------------------------------------------


class JsonSkillsetRepository:
    """Read-only skillset repository backed by a single JSON file."""

    def __init__(self, skillsets_root: Path) -> None:
        self._file = skillsets_root / "index.json"

    def _load(self) -> list[Skillset]:
        return [Skillset.model_validate(item) for item in _read_json_array(self._file)]

    def get(self, name: str) -> Skillset | None:
        for s in self._load():
            if s.name == name:
                return s
        return None

    def list_all(self) -> list[Skillset]:
        return self._load()


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


class JsonProjectRepository:
    """Project repository. One index.json per client under projects/."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root

    def _file(self, client: str) -> Path:
        return self._root / client / "projects" / "index.json"

    def _load(self, client: str) -> list[Project]:
        return [
            Project.model_validate(item)
            for item in _read_json_array(self._file(client))
        ]

    def _persist(self, client: str, projects: list[Project]) -> None:
        _write_json_array(
            self._file(client),
            [p.model_dump(mode="json") for p in projects],
        )

    def get(self, client: str, slug: str) -> Project | None:
        for p in self._load(client):
            if p.slug == slug:
                return p
        return None

    def list_all(self, client: str) -> list[Project]:
        return self._load(client)

    def list_filtered(
        self,
        client: str,
        skillset: str | None = None,
        status: ProjectStatus | None = None,
    ) -> list[Project]:
        projects = self._load(client)
        if skillset is not None:
            projects = [p for p in projects if p.skillset == skillset]
        if status is not None:
            projects = [p for p in projects if p.status == status]
        return projects

    def save(self, project: Project) -> None:
        projects = self._load(project.client)
        for i, p in enumerate(projects):
            if p.slug == project.slug:
                projects[i] = project
                self._persist(project.client, projects)
                return
        projects.append(project)
        self._persist(project.client, projects)

    def delete(self, client: str, slug: str) -> bool:
        projects = self._load(client)
        filtered = [p for p in projects if p.slug != slug]
        if len(filtered) == len(projects):
            return False
        self._persist(client, filtered)
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

    def _file(self, client: str, project_slug: str) -> Path:
        return self._root / client / "projects" / project_slug / "decisions.json"

    def _load(self, client: str, project_slug: str) -> list[DecisionEntry]:
        return [
            DecisionEntry.model_validate(item)
            for item in _read_json_array(self._file(client, project_slug))
        ]

    def get(self, client: str, project_slug: str, id: str) -> DecisionEntry | None:
        for d in self._load(client, project_slug):
            if d.id == id:
                return d
        return None

    def list_all(self, client: str, project_slug: str) -> list[DecisionEntry]:
        return self._load(client, project_slug)

    def list_filtered(
        self,
        client: str,
        project_slug: str,
        title: str | None = None,
    ) -> list[DecisionEntry]:
        entries = self._load(client, project_slug)
        if title is not None:
            entries = [e for e in entries if e.title == title]
        return entries

    def save(self, entry: DecisionEntry) -> None:
        path = self._file(entry.client, entry.project_slug)
        entries = _read_json_array(path)
        entries.append(entry.model_dump(mode="json"))
        _write_json_array(path, entries)


# ---------------------------------------------------------------------------
# Engagement
# ---------------------------------------------------------------------------


class JsonEngagementRepository:
    """Append-only engagement repository. One file per client."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root

    def _file(self, client: str) -> Path:
        return self._root / client / "engagement.json"

    def _load(self, client: str) -> list[EngagementEntry]:
        return [
            EngagementEntry.model_validate(item)
            for item in _read_json_array(self._file(client))
        ]

    def get(self, client: str, id: str) -> EngagementEntry | None:
        for e in self._load(client):
            if e.id == id:
                return e
        return None

    def list_all(self, client: str) -> list[EngagementEntry]:
        return self._load(client)

    def save(self, entry: EngagementEntry) -> None:
        path = self._file(entry.client)
        entries = _read_json_array(path)
        entries.append(entry.model_dump(mode="json"))
        _write_json_array(path, entries)


# ---------------------------------------------------------------------------
# Research topic
# ---------------------------------------------------------------------------


class JsonResearchTopicRepository:
    """Research topic repository. One index.json per client under resources/."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root

    def _file(self, client: str) -> Path:
        return self._root / client / "resources" / "index.json"

    def _load(self, client: str) -> list[ResearchTopic]:
        return [
            ResearchTopic.model_validate(item)
            for item in _read_json_array(self._file(client))
        ]

    def _persist(self, client: str, topics: list[ResearchTopic]) -> None:
        _write_json_array(
            self._file(client),
            [t.model_dump(mode="json") for t in topics],
        )

    def get(self, client: str, filename: str) -> ResearchTopic | None:
        for t in self._load(client):
            if t.filename == filename:
                return t
        return None

    def list_all(self, client: str) -> list[ResearchTopic]:
        return self._load(client)

    def save(self, topic: ResearchTopic) -> None:
        topics = self._load(topic.client)
        for i, t in enumerate(topics):
            if t.filename == topic.filename:
                topics[i] = topic
                self._persist(topic.client, topics)
                return
        topics.append(topic)
        self._persist(topic.client, topics)

    def exists(self, client: str, filename: str) -> bool:
        return any(t.filename == filename for t in self._load(client))


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
