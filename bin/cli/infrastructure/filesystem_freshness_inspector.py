"""Filesystem implementation of the FreshnessInspector protocol.

Walks the pack directory tree and compares SHA-256 content hashes
stored in bytecode frontmatter against live source content to
determine compilation freshness. Stateless — pack_root is passed
per call.
"""

from __future__ import annotations

from pathlib import Path

from practice.content_hash import hash_children, hash_content
from practice.entities import CompilationState, ItemFreshness, PackFreshness
from practice.frontmatter import split_frontmatter

# Files at the pack root that are not compilable source items.
_EXCLUDED_NAMES = {"index.md", "summary.md"}


class FilesystemFreshnessInspector:
    """Assess compilation freshness of a knowledge pack on disk."""

    def assess(self, pack_root: Path) -> PackFreshness:
        bytecode_dir = pack_root / "_bytecode"

        # --- Discover source items ---
        source_items: list[Path] = []
        child_packs: list[Path] = []

        for entry in sorted(pack_root.iterdir()):
            if entry.name.startswith("_") or entry.name.startswith("."):
                continue
            if entry.is_dir():
                if (entry / "index.md").is_file():
                    child_packs.append(entry)
                # Non-pack directories are ignored
                continue
            if entry.suffix == ".md" and entry.name not in _EXCLUDED_NAMES:
                source_items.append(entry)

        # --- ABSENT: no _bytecode/ directory ---
        if not bytecode_dir.is_dir():
            items = [
                ItemFreshness(name=p.stem, is_composite=False, state="absent")
                for p in source_items
            ]
            children = [self.assess(cp) for cp in child_packs]
            items.extend(
                ItemFreshness(name=cp.name, is_composite=True, state="absent")
                for cp in child_packs
            )
            return PackFreshness(
                pack_root=str(pack_root),
                compilation_state=CompilationState.ABSENT,
                items=items,
                children=children,
            )

        # --- Assess each leaf item ---
        items: list[ItemFreshness] = []
        for item_path in source_items:
            mirror = bytecode_dir / f"{item_path.stem}.md"
            if not mirror.is_file():
                items.append(
                    ItemFreshness(
                        name=item_path.stem, is_composite=False, state="absent"
                    )
                )
            else:
                meta, _ = split_frontmatter(mirror.read_text())
                expected = hash_content(item_path.read_text())
                if meta.get("source_hash") == expected:
                    items.append(
                        ItemFreshness(
                            name=item_path.stem, is_composite=False, state="clean"
                        )
                    )
                else:
                    items.append(
                        ItemFreshness(
                            name=item_path.stem, is_composite=False, state="dirty"
                        )
                    )

        # --- Assess each composite item (child pack) ---
        children: list[PackFreshness] = []
        for child_path in child_packs:
            child_freshness = self.assess(child_path)
            children.append(child_freshness)

            mirror = bytecode_dir / f"{child_path.name}.md"
            if not mirror.is_file():
                items.append(
                    ItemFreshness(
                        name=child_path.name, is_composite=True, state="absent"
                    )
                )
            elif child_freshness.deep_state != CompilationState.CLEAN:
                # Child will change after recompilation → parent summary stale
                items.append(
                    ItemFreshness(
                        name=child_path.name, is_composite=True, state="dirty"
                    )
                )
            else:
                # Child is clean — check if parent's hash matches child bytecode
                child_bytecode = child_path / "_bytecode"
                if child_bytecode.is_dir():
                    meta, _ = split_frontmatter(mirror.read_text())
                    expected = hash_children(child_bytecode)
                    if meta.get("source_hash") == expected:
                        items.append(
                            ItemFreshness(
                                name=child_path.name,
                                is_composite=True,
                                state="clean",
                            )
                        )
                    else:
                        items.append(
                            ItemFreshness(
                                name=child_path.name,
                                is_composite=True,
                                state="dirty",
                            )
                        )
                else:
                    items.append(
                        ItemFreshness(
                            name=child_path.name, is_composite=True, state="clean"
                        )
                    )

        # --- Check for orphan mirrors ---
        source_names = {p.stem for p in source_items}
        child_names = {p.name for p in child_packs}
        all_known = source_names | child_names

        for bc_file in sorted(bytecode_dir.iterdir()):
            if bc_file.suffix == ".md" and bc_file.stem not in all_known:
                items.append(
                    ItemFreshness(name=bc_file.stem, is_composite=False, state="orphan")
                )

        # --- Roll up ---
        has_orphan = any(i.state == "orphan" for i in items)
        has_dirty_or_absent = any(i.state in ("dirty", "absent") for i in items)

        if has_orphan:
            state = CompilationState.CORRUPT
        elif has_dirty_or_absent:
            state = CompilationState.DIRTY
        else:
            state = CompilationState.CLEAN

        return PackFreshness(
            pack_root=str(pack_root),
            compilation_state=state,
            items=items,
            children=children,
        )
