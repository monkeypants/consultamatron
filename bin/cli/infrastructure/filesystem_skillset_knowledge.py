"""Filesystem adapter for SkillsetKnowledge port.

Reads typed knowledge items from a skillset's docs/ pack,
preferring _bytecode/ summaries over raw source files.
"""

from __future__ import annotations

from pathlib import Path

from practice.frontmatter import split_frontmatter


class FilesystemSkillsetKnowledge:
    """Read knowledge items from skillset docs packs on disk.

    Each skillset's bounded context directory contains a docs/ pack.
    Items are identified by type (e.g. "pantheon", "patterns").
    Bytecode summaries take priority over raw source files.
    """

    def __init__(self, skillset_bc_dirs: dict[str, Path]) -> None:
        self._skillset_bc_dirs = skillset_bc_dirs

    def read_item(self, skillset_name: str, item_type: str) -> str | None:
        bc_dir = self._skillset_bc_dirs.get(skillset_name)
        if bc_dir is None:
            return None

        docs = bc_dir / "docs"
        bytecode_path = docs / "_bytecode" / f"{item_type}.md"
        source_path = docs / f"{item_type}.md"

        for path in (bytecode_path, source_path):
            if path.is_file():
                text = path.read_text()
                _, body = split_frontmatter(text)
                return body

        return None
