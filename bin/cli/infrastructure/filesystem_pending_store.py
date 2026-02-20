"""PendingObservationStore backed by filesystem.

Reads and clears markdown observation files from the
``.observations-pending/`` staging directory within an engagement.
"""

from __future__ import annotations

from pathlib import Path

from practice.entities import Observation
from practice.frontmatter import parse_frontmatter


class FilesystemPendingObservationStore:
    """Read/clear pending observations from .observations-pending/ dirs."""

    def __init__(self, workspace_root: Path) -> None:
        self._workspace_root = workspace_root

    def read_pending(self, client: str, engagement: str) -> list[Observation]:
        """Read all pending observation files for an engagement."""
        pending_dir = self._pending_dir(client, engagement)
        if not pending_dir.is_dir():
            return []
        results: list[Observation] = []
        for md_file in sorted(pending_dir.glob("*.md")):
            obs = self._parse_pending(md_file)
            if obs is not None:
                results.append(obs)
        return results

    def clear_pending(self, client: str, engagement: str) -> None:
        """Remove all .md files from the pending directory."""
        pending_dir = self._pending_dir(client, engagement)
        if not pending_dir.is_dir():
            return
        for md_file in pending_dir.glob("*.md"):
            md_file.unlink()

    def _pending_dir(self, client: str, engagement: str) -> Path:
        return (
            self._workspace_root
            / client
            / "engagements"
            / engagement
            / ".observations-pending"
        )

    def _parse_pending(self, path: Path) -> Observation | None:
        """Parse a pending observation markdown file."""
        fm = parse_frontmatter(path)
        if not fm or "slug" not in fm:
            return None

        # Body is everything after the second ---
        text = path.read_text()
        parts = text.split("---", 2)
        body = parts[2].strip() if len(parts) >= 3 else ""

        need_refs = fm.get("need_refs", [])
        if isinstance(need_refs, str):
            need_refs = [r.strip() for r in need_refs.split(",") if r.strip()]

        return Observation(
            slug=fm["slug"],
            source_inflection=fm.get("source_inflection", ""),
            need_refs=need_refs,
            content=body,
            destinations=[],  # Resolved at flush time
        )
