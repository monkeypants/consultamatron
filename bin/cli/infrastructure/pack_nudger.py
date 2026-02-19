"""Check design-time packs for freshness and produce nudge strings.

Discovers knowledge packs via ``FilesystemKnowledgePackRepository``
and checks each for bytecode freshness. Returns human-readable nudge
strings for any pack that is dirty or corrupt.
"""

from __future__ import annotations

from pathlib import Path

from bin.cli.infrastructure.filesystem_knowledge_pack_repository import (
    FilesystemKnowledgePackRepository,
)
from practice.entities import CompilationState
from practice.repositories import FreshnessInspector


_STATE_LABELS = {
    CompilationState.DIRTY: "has stale bytecode",
    CompilationState.CORRUPT: "has orphan bytecode mirrors",
    CompilationState.ABSENT: "has no compiled bytecode",
}


class FilesystemPackNudger:
    """Check design-time packs and return nudge strings."""

    def __init__(
        self,
        repo_root: Path,
        inspector: FreshnessInspector,
        skillset_bc_dirs: dict[str, Path] | None = None,
        knowledge_packs: FilesystemKnowledgePackRepository | None = None,
    ) -> None:
        self._repo_root = repo_root
        self._inspector = inspector
        self._skillset_bc_dirs = skillset_bc_dirs or {}
        self._knowledge_packs = knowledge_packs

    def check(self, skillset_names: list[str] | None = None) -> list[str]:
        if self._knowledge_packs is not None:
            packs = [
                (pack.name, path)
                for pack, path in self._knowledge_packs.packs_with_paths()
            ]
        else:
            packs = _discover_packs(self._repo_root)

        nudges: list[str] = []

        relevant_bc_dirs: set[Path] | None = None
        if skillset_names is not None:
            relevant_bc_dirs = {
                self._skillset_bc_dirs[n]
                for n in skillset_names
                if n in self._skillset_bc_dirs
            }

        docs_root = self._repo_root / "docs"

        for name, pack_root in packs:
            if relevant_bc_dirs is not None:
                is_platform = pack_root.is_relative_to(docs_root)
                is_relevant_bc = any(
                    pack_root.is_relative_to(d) for d in relevant_bc_dirs
                )
                if not is_platform and not is_relevant_bc:
                    continue

            freshness = self._inspector.assess(pack_root)
            state = freshness.deep_state
            if state == CompilationState.CLEAN:
                continue
            label = _STATE_LABELS.get(state, str(state))
            rel = pack_root.relative_to(self._repo_root)
            nudges.append(
                f"Knowledge pack '{name}' ({rel}) {label}. "
                f"Run: practice pack status --path {rel}"
            )

        return nudges


def _discover_packs(repo_root: Path) -> list[tuple[str, Path]]:
    """Find all version-controlled packs with manifest frontmatter.

    Legacy fallback — used when no knowledge pack repository is injected.
    """
    from practice.frontmatter import parse_frontmatter

    results: list[tuple[str, Path]] = []
    search_roots = [repo_root / "docs", repo_root / "commons"]

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
        for index_md in search_root.rglob("index.md"):
            fm = parse_frontmatter(index_md)
            if "name" in fm and "purpose" in fm:
                results.append((fm["name"], index_md.parent))
    return results
