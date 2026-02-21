"""ProfileRepository that reads skillset-profiles.json from each source.

Scans source containers for profile definitions:
- ``commons/{org}/{repo}/skillsets/skillset-profiles.json`` (each submodule)
- ``personal/skillsets/skillset-profiles.json`` (personal)
- ``partnerships/{slug}/skillsets/skillset-profiles.json`` (each partnership)

Validates that each profile only references skillsets from its own source.
Invalid profiles are skipped at load time.
"""

from __future__ import annotations

import json
from pathlib import Path

from practice.entities import Profile
from practice.repositories import SourceRepository


class FilesystemProfileRepository:
    """ProfileRepository backed by skillset-profiles.json files."""

    def __init__(self, repo_root: Path, sources: SourceRepository) -> None:
        self._repo_root = repo_root
        self._sources = sources
        self._profiles: list[tuple[Profile, str]] = self._load_all()

    def get(self, name: str) -> tuple[Profile, str] | None:
        for profile, source_slug in self._profiles:
            if profile.name == name:
                return (profile, source_slug)
        return None

    def list_all(self) -> list[tuple[Profile, str]]:
        return list(self._profiles)

    def _load_all(self) -> list[tuple[Profile, str]]:
        results: list[tuple[Profile, str]] = []

        # Commons: commons/{org}/{repo}/skillsets/skillset-profiles.json
        commons = self._repo_root / "commons"
        if commons.is_dir():
            for org in sorted(commons.iterdir()):
                if not org.is_dir() or org.name.startswith("."):
                    continue
                for repo in sorted(org.iterdir()):
                    if not repo.is_dir():
                        continue
                    path = repo / "skillsets" / "skillset-profiles.json"
                    results.extend(self._load_file(path, "commons"))

        # Personal: personal/skillsets/skillset-profiles.json
        results.extend(
            self._load_file(
                self._repo_root / "personal" / "skillsets" / "skillset-profiles.json",
                "personal",
            )
        )

        # Partnerships: partnerships/{slug}/skillsets/skillset-profiles.json
        partnerships_dir = self._repo_root / "partnerships"
        if partnerships_dir.is_dir():
            for subdir in sorted(partnerships_dir.iterdir()):
                if subdir.is_dir():
                    results.extend(
                        self._load_file(
                            subdir / "skillsets" / "skillset-profiles.json",
                            subdir.name,
                        )
                    )

        return results

    def _load_file(self, path: Path, source_slug: str) -> list[tuple[Profile, str]]:
        if not path.is_file():
            return []

        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return []

        source = self._sources.get(source_slug)
        allowed_names = set(source.skillset_names) if source else set()

        results: list[tuple[Profile, str]] = []
        for item in data:
            try:
                profile = Profile(**item)
            except Exception:
                continue
            if all(s in allowed_names for s in profile.skillsets):
                results.append((profile, source_slug))

        return results
