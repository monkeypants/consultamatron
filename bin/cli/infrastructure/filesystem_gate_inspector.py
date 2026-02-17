"""Filesystem implementation of the GateInspector protocol.

Checks gate artifact existence by resolving paths under the workspace
root: {workspace_root}/{client}/engagements/{engagement}/{project}/{gate_path}
"""

from __future__ import annotations

from pathlib import Path


class FilesystemGateInspector:
    """Check gate artifact existence on the local filesystem."""

    def __init__(self, workspace_root: Path) -> None:
        self._workspace_root = workspace_root

    def exists(
        self, client: str, engagement: str, project: str, gate_path: str
    ) -> bool:
        path = (
            self._workspace_root
            / client
            / "engagements"
            / engagement
            / project
            / gate_path
        )
        return path.is_file()
