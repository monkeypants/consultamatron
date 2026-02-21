"""Workspace path conventions.

Maps logical locations to filesystem paths, following the
directory structure used by skills:

    clients/
    └── {client}/                          # directory name = client ID
        ├── index.json                     # client metadata
        ├── engagement.json                # engagement log entries
        ├── resources/
        │   └── index.json                 # research topic manifest
        └── projects/
            ├── index.json                 # project list
            └── {project-slug}/
                ├── decisions.json         # decision log entries
                └── presentations/
                    └── {tour-name}/
                        └── manifest.json  # tour manifest

The clients/ directory itself is the client registry — listing
its subdirectories lists all clients. Renaming a directory
renames the client. No file duplicates that information.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Root paths for the workspace."""

    repo_root: Path
    workspace_root: Path

    @classmethod
    def from_repo_root(cls, repo_root: Path) -> Config:
        return cls(
            repo_root=repo_root,
            workspace_root=repo_root / "clients",
        )
