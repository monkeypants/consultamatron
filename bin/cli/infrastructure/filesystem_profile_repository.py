"""ProfileRepository that reads skillset-profiles.json from each source.

Scans three locations for profile definitions:
- ``{repo_root}/skillset-profiles.json`` (commons)
- ``{repo_root}/personal/skillset-profiles.json`` (personal)
- ``{repo_root}/partnerships/{slug}/skillset-profiles.json`` (each partnership)

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

        # Commons
        results.extend(
            self._load_file(self._repo_root / "skillset-profiles.json", "commons")
        )

        # Personal
        results.extend(
            self._load_file(
                self._repo_root / "personal" / "skillset-profiles.json", "personal"
            )
        )

        # Partnerships
        partnerships_dir = self._repo_root / "partnerships"
        if partnerships_dir.is_dir():
            for subdir in sorted(partnerships_dir.iterdir()):
                if subdir.is_dir():
                    results.extend(
                        self._load_file(subdir / "skillset-profiles.json", subdir.name)
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
