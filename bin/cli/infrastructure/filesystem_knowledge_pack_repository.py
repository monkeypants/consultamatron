"""KnowledgePackRepository backed by index.md manifests on disk.

Scans ``docs/``, ``commons/``, ``personal/``, and each
``partnerships/{slug}/`` for ``**/index.md`` files with YAML
frontmatter containing at least ``name`` and ``purpose``.
Validates each via ``KnowledgePack.model_validate()``.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from practice.entities import KnowledgePack
from practice.frontmatter import parse_frontmatter


class FilesystemKnowledgePackRepository:
    """Aggregates knowledge pack manifests from version-controlled dirs."""

    def __init__(self, repo_root: Path) -> None:
        self._packs: list[tuple[KnowledgePack, Path]] = []
        search_roots: list[Path] = [repo_root / "docs", repo_root / "commons"]

        personal = repo_root / "personal"
        if personal.is_dir():
            search_roots.append(personal)

        partnerships = repo_root / "partnerships"
        if partnerships.is_dir():
            for child in sorted(partnerships.iterdir()):
                if child.is_dir():
                    search_roots.append(child)

        for search_root in search_roots:
            if not search_root.is_dir():
                continue
            for index_md in sorted(search_root.rglob("index.md")):
                fm = parse_frontmatter(index_md)
                if "name" not in fm or "purpose" not in fm:
                    continue
                try:
                    pack = KnowledgePack.model_validate(fm)
                except (ValidationError, TypeError):
                    continue
                self._packs.append((pack, index_md.parent))

    def get(self, name: str) -> KnowledgePack | None:
        for pack, _ in self._packs:
            if pack.name == name:
                return pack
        return None

    def list_all(self) -> list[KnowledgePack]:
        return [pack for pack, _ in self._packs]

    def packs_with_paths(self) -> list[tuple[KnowledgePack, Path]]:
        """Return (pack, pack_root) pairs — used by the nudger."""
        return list(self._packs)
