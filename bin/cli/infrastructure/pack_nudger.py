"""Check design-time packs for freshness and produce nudge strings.

Discovers knowledge packs under docs/ and commons/ (plus personal/ and
partnerships/) by scanning for index.md manifests with name + purpose
frontmatter. Returns human-readable nudge strings for any pack that is
dirty or corrupt.
"""

from __future__ import annotations

from pathlib import Path

from practice.entities import CompilationState
from practice.repositories import FreshnessInspector


def _parse_manifest_frontmatter(index_path: Path) -> dict:
    """Extract frontmatter key-value pairs from an index.md file.

    Minimal parser — handles flat ``key: value`` pairs and the YAML
    ``>`` folded-scalar continuation.  No external YAML dependency.
    """
    text = index_path.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}

    result: dict[str, str] = {}
    current_key: str | None = None
    folding = False
    fold_lines: list[str] = []

    for line in parts[1].splitlines():
        stripped = line.strip()
        if not stripped:
            if folding:
                fold_lines.append("")
            continue

        # Indented continuation of a folded scalar
        if folding and line[0] in (" ", "\t"):
            fold_lines.append(stripped)
            continue

        # Flush any accumulated folded text
        if folding:
            result[current_key] = " ".join(ln for ln in fold_lines if ln)
            folding = False
            fold_lines = []

        if ":" not in stripped:
            continue

        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()

        if value == ">":
            current_key = key
            folding = True
            fold_lines = []
        elif value:
            result[key] = value
        else:
            result[key] = ""

    # Flush trailing folded scalar
    if folding:
        result[current_key] = " ".join(ln for ln in fold_lines if ln)

    return result


def _discover_packs(repo_root: Path) -> list[tuple[str, Path]]:
    """Find all version-controlled packs with manifest frontmatter."""
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
            fm = _parse_manifest_frontmatter(index_md)
            if "name" in fm and "purpose" in fm:
                results.append((fm["name"], index_md.parent))
    return results


_STATE_LABELS = {
    CompilationState.DIRTY: "has stale bytecode",
    CompilationState.CORRUPT: "has orphan bytecode mirrors",
    CompilationState.ABSENT: "has no compiled bytecode",
}


class FilesystemPackNudger:
    """Check design-time packs and return nudge strings."""

    def __init__(self, repo_root: Path, inspector: FreshnessInspector) -> None:
        self._repo_root = repo_root
        self._inspector = inspector

    def check(self, skillset_names: list[str] | None = None) -> list[str]:
        packs = _discover_packs(self._repo_root)
        nudges: list[str] = []

        for name, pack_root in packs:
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
