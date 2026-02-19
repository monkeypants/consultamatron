"""Pack-and-wrap orchestration for knowledge packs.

Compiles dirty items in a knowledge pack by delegating to an
ItemCompiler and tracking state transitions via FreshnessInspector.
This is convention-layer infrastructure, not a consulting use case.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from practice.entities import CompilationState
from practice.repositories import FreshnessInspector, ItemCompiler


class PackAndWrapResult(BaseModel):
    compiled_items: list[str]
    deleted_orphans: list[str]
    state_before: CompilationState
    state_after: CompilationState


def pack_and_wrap(
    pack_root: Path,
    inspector: FreshnessInspector,
    compiler: ItemCompiler,
    *,
    deep: bool = True,
) -> PackAndWrapResult:
    """Compile dirty items in a knowledge pack.

    When deep=True, processes nested packs bottom-up first.
    """
    freshness = inspector.assess(pack_root)
    state_before = freshness.deep_state if deep else freshness.compilation_state

    compiled_items: list[str] = []
    deleted_orphans: list[str] = []

    # --- Deep: recursively compile children bottom-up ---
    if deep:
        for child in freshness.children:
            child_root = Path(child.pack_root)
            if child.deep_state != CompilationState.CLEAN:
                child_result = pack_and_wrap(child_root, inspector, compiler, deep=True)
                compiled_items.extend(child_result.compiled_items)
                deleted_orphans.extend(child_result.deleted_orphans)

    bytecode_dir = pack_root / "_bytecode"

    # --- Delete orphan mirrors ---
    for item in freshness.items:
        if item.state == "orphan":
            orphan_path = bytecode_dir / f"{item.name}.md"
            if orphan_path.is_file():
                orphan_path.unlink()
                deleted_orphans.append(item.name)

    # --- Create _bytecode/ if absent ---
    bytecode_dir.mkdir(exist_ok=True)

    # --- Compile dirty/absent items ---
    for item in freshness.items:
        if item.state in ("dirty", "absent"):
            if item.is_composite:
                # For composite items, the item_path is the child directory
                item_path = pack_root / item.name
            else:
                item_path = pack_root / f"{item.name}.md"

            summary = compiler.compile(item_path, pack_root)
            mirror = bytecode_dir / f"{item.name}.md"
            mirror.write_text(summary)
            compiled_items.append(item.name)

    # --- Re-assess for final state ---
    final_freshness = inspector.assess(pack_root)
    state_after = (
        final_freshness.deep_state if deep else final_freshness.compilation_state
    )

    return PackAndWrapResult(
        compiled_items=compiled_items,
        deleted_orphans=deleted_orphans,
        state_before=state_before,
        state_after=state_after,
    )
