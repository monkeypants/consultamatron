"""JSON file-backed repository implementations.

Each implementation takes a root path in its constructor and
derives file locations following the workspace conventions
defined in config.py. The directory structure carries semantic
meaning — the client ID is the directory name, not a field in
a file.

    {workspace_root}/
    └── {client}/
        ├── index.json
        ├── engagement-log.json
        ├── resources/
        │   └── index.json
        └── engagements/
            ├── index.json
            └── {engagement-slug}/
                ├── projects.json
                └── {project-slug}/
                    ├── decisions.json
                    └── presentations/
                        └── {tour-name}/
                            └── manifest.json

    {skillsets_root}/
    └── index.json
"""

from __future__ import annotations

from pathlib import Path

from practice.entities import DecisionEntry, EngagementEntry
from practice.entities import (
    Engagement,
    Pipeline,
    Project,
    ProjectStatus,
    ResearchTopic,
)
from bin.cli.infrastructure.json_store import (
    JsonArrayStore,
)


# ---------------------------------------------------------------------------
# Skillset
# ---------------------------------------------------------------------------


class JsonSkillsetRepository:
    """Read-only pipeline repository backed by a single JSON file."""

    def __init__(self, skillsets_root: Path) -> None:
        self._store: JsonArrayStore[Pipeline] = JsonArrayStore(Pipeline, "name")
        self._file = skillsets_root / "index.json"

    def get(self, name: str) -> Pipeline | None:
        return self._store.find(self._store.load(self._file), name)

    def list_all(self) -> list[Pipeline]:
        return self._store.load(self._file)


# ---------------------------------------------------------------------------
# Engagement entity (mutable CRUD)
# ---------------------------------------------------------------------------


class JsonEngagementEntityRepository:
    """Engagement entity repository. One index.json per client."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root
        self._store: JsonArrayStore[Engagement] = JsonArrayStore(Engagement, "slug")

    def _file(self, client: str) -> Path:
        return self._root / client / "engagements" / "index.json"

    def get(self, client: str, slug: str) -> Engagement | None:
        return self._store.find(self._store.load(self._file(client)), slug)

    def list_all(self, client: str) -> list[Engagement]:
        return self._store.load(self._file(client))

    def save(self, engagement: Engagement) -> None:
        self._store.upsert(self._file(engagement.client), engagement)


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


class JsonProjectRepository:
    """Project repository. One projects.json per engagement."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root
        self._store: JsonArrayStore[Project] = JsonArrayStore(Project, "slug")

    def _file(self, client: str, engagement: str) -> Path:
        return self._root / client / "engagements" / engagement / "projects.json"

    def get(self, client: str, engagement: str, slug: str) -> Project | None:
        return self._store.find(self._store.load(self._file(client, engagement)), slug)

    def list_all(self, client: str) -> list[Project]:
        """List all projects across all engagements for a client."""
        eng_dir = self._root / client / "engagements"
        if not eng_dir.is_dir():
            return []
        projects: list[Project] = []
        for sub in sorted(eng_dir.iterdir()):
            if not sub.is_dir():
                continue
            proj_file = sub / "projects.json"
            projects.extend(self._store.load(proj_file))
        return projects

    def list_filtered(
        self,
        client: str,
        engagement: str,
        skillset: str | None = None,
        status: ProjectStatus | None = None,
    ) -> list[Project]:
        projects = self._store.load(self._file(client, engagement))
        if skillset is not None:
            projects = [p for p in projects if p.skillset == skillset]
        if status is not None:
            projects = [p for p in projects if p.status == status]
        return projects

    def save(self, project: Project) -> None:
        self._store.upsert(self._file(project.client, project.engagement), project)

    def delete(self, client: str, engagement: str, slug: str) -> bool:
        path = self._file(client, engagement)
        items = self._store.load(path)
        filtered = [p for p in items if p.slug != slug]
        if len(filtered) == len(items):
            return False
        self._store.persist(path, filtered)
        return True

    def client_exists(self, client: str) -> bool:
        return (self._root / client).is_dir()

    def list_clients(self) -> list[str]:
        if not self._root.is_dir():
            return []
        return sorted(
            d.name
            for d in self._root.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------


class JsonDecisionRepository:
    """Append-only decision repository. One file per project."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root
        self._store: JsonArrayStore[DecisionEntry] = JsonArrayStore(DecisionEntry, "id")

    def _file(self, client: str, engagement: str, project_slug: str) -> Path:
        return (
            self._root
            / client
            / "engagements"
            / engagement
            / project_slug
            / "decisions.json"
        )

    def get(
        self, client: str, engagement: str, project_slug: str, id: str
    ) -> DecisionEntry | None:
        return self._store.find(
            self._store.load(self._file(client, engagement, project_slug)), id
        )

    def list_all(
        self, client: str, engagement: str, project_slug: str
    ) -> list[DecisionEntry]:
        return self._store.load(self._file(client, engagement, project_slug))

    def list_filtered(
        self,
        client: str,
        engagement: str,
        project_slug: str,
        title: str | None = None,
    ) -> list[DecisionEntry]:
        entries = self._store.load(self._file(client, engagement, project_slug))
        if title is not None:
            entries = [e for e in entries if e.title == title]
        return entries

    def save(self, entry: DecisionEntry) -> None:
        self._store.append(
            self._file(entry.client, entry.engagement, entry.project_slug), entry
        )


# ---------------------------------------------------------------------------
# Engagement log (append-only audit trail)
# ---------------------------------------------------------------------------


class JsonEngagementLogRepository:
    """Append-only engagement log repository. One file per client."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root
        self._store: JsonArrayStore[EngagementEntry] = JsonArrayStore(
            EngagementEntry, "id"
        )

    def _file(self, client: str) -> Path:
        return self._root / client / "engagement-log.json"

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
