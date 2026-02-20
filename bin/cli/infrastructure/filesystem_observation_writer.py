"""ObservationWriter backed by filesystem.

Writes one markdown file per destination for each observation.
Files are placed in the destination's observations directory.

Path conventions:

| Owner type  | Path                                                        |
|-------------|-------------------------------------------------------------|
| client      | {workspace_root}/{ref}/observations/*.md                    |
| personal    | {repo_root}/personal/observations/*.md                      |
| practice    | {repo_root}/docs/observations/*.md                          |
| engagement  | {workspace_root}/{client}/engagements/{eng}/observations/*.md |
"""

from __future__ import annotations

from pathlib import Path

from practice.entities import Observation, RoutingDestination


class FilesystemObservationWriter:
    """Write observations to filesystem destinations."""

    def __init__(self, repo_root: Path, workspace_root: Path) -> None:
        self._repo_root = repo_root
        self._workspace_root = workspace_root

    def write(self, observation: Observation) -> None:
        """Write observation to all resolved destinations."""
        for dest in observation.destinations:
            obs_dir = self._destination_dir(dest)
            if obs_dir is None:
                continue
            obs_dir.mkdir(parents=True, exist_ok=True)
            path = obs_dir / f"{observation.slug}.md"
            path.write_text(self._render(observation))

    def _destination_dir(self, dest: RoutingDestination) -> Path | None:
        """Resolve the observations directory for a destination."""
        if dest.owner_type == "client":
            return self._workspace_root / dest.owner_ref / "observations"
        if dest.owner_type == "personal":
            return self._repo_root / "personal" / "observations"
        if dest.owner_type == "practice":
            return self._repo_root / "docs" / "observations"
        return None

    def _render(self, observation: Observation) -> str:
        """Render an observation as markdown with frontmatter."""
        lines = [
            "---",
            f"slug: {observation.slug}",
            f"source_inflection: {observation.source_inflection}",
            f"need_refs: [{', '.join(observation.need_refs)}]",
            "---",
            "",
            observation.content,
            "",
        ]
        return "\n".join(lines)
