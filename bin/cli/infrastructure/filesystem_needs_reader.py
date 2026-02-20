"""NeedsReader backed by filesystem scanning.

Reads observation need declarations from markdown files with YAML
frontmatter. Type-level needs live in ``docs/observation-needs/``,
instance-level needs live with their owner.

Path conventions:

| Level    | Owner type  | Path                                                       |
|----------|-------------|------------------------------------------------------------|
| type     | any         | {repo_root}/docs/observation-needs/{owner_type}.md         |
| instance | client      | {workspace_root}/{client}/observation-needs/*.md           |
| instance | engagement  | {workspace_root}/{client}/engagements/{eng}/obs-needs/*.md |
| instance | personal    | {repo_root}/personal/observation-needs/*.md                |
| instance | practice    | {repo_root}/docs/observation-needs/*.md                    |
"""

from __future__ import annotations

from pathlib import Path

from practice.entities import ObservationNeed
from practice.frontmatter import parse_frontmatter


class FilesystemNeedsReader:
    """Read observation needs from the filesystem."""

    def __init__(self, repo_root: Path, workspace_root: Path) -> None:
        self._repo_root = repo_root
        self._workspace_root = workspace_root

    def type_level_needs(self, owner_type: str) -> list[ObservationNeed]:
        """Read the single type-level needs file for an owner type."""
        path = self._repo_root / "docs" / "observation-needs" / f"{owner_type}.md"
        if not path.is_file():
            return []
        return self._parse_need_file(path)

    def instance_needs(self, owner_type: str, owner_ref: str) -> list[ObservationNeed]:
        """Read all instance-level need files for a specific owner."""
        needs_dir = self._instance_needs_dir(owner_type, owner_ref)
        if needs_dir is None or not needs_dir.is_dir():
            return []
        results: list[ObservationNeed] = []
        for md_file in sorted(needs_dir.glob("*.md")):
            results.extend(self._parse_need_file(md_file))
        return results

    def _instance_needs_dir(self, owner_type: str, owner_ref: str) -> Path | None:
        """Resolve the directory containing instance-level needs."""
        if owner_type == "client":
            return self._workspace_root / owner_ref / "observation-needs"
        if owner_type == "personal":
            return self._repo_root / "personal" / "observation-needs"
        if owner_type == "practice":
            return self._repo_root / "docs" / "observation-needs"
        return None

    def _parse_need_file(self, path: Path) -> list[ObservationNeed]:
        """Parse a single needs markdown file into an ObservationNeed."""
        fm = parse_frontmatter(path)
        if not fm or "slug" not in fm:
            return []
        served = fm.get("served", False)
        if isinstance(served, str):
            served = served.lower() in ("true", "yes", "1")
        return [
            ObservationNeed(
                slug=fm["slug"],
                owner_type=fm.get("owner_type", ""),
                owner_ref=fm.get("owner_ref", ""),
                level=fm.get("level", ""),
                need=fm.get("need", ""),
                rationale=fm.get("rationale", ""),
                lifecycle_moment=fm.get("lifecycle_moment", ""),
                served=bool(served),
            )
        ]
