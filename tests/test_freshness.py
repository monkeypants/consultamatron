"""Freshness detection, nested traversal, and pack-and-wrap orchestration.

Three Beck test phases:
  1. Freshness detection — filesystem state → CompilationState
  2. Nested freshness — deep traversal and transitive rollup
  3. Pack-and-wrap orchestration — compilation workflow
"""

from __future__ import annotations

import pytest

from bin.cli.infrastructure.filesystem_freshness_inspector import (
    FilesystemFreshnessInspector,
)
from practice.entities import CompilationState
from practice.pack_and_wrap import pack_and_wrap

from .conftest import StubCompiler, age_file, freshen_file, write_pack


# ---------------------------------------------------------------------------
# Phase 1: Freshness detection (filesystem → CompilationState)
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestFreshnessDetection:
    """Single-level freshness assessment from filesystem state."""

    def test_no_bytecode_dir_is_absent(self, tmp_path):
        """Pack with index.md + items, no _bytecode/ → ABSENT."""
        root = write_pack(tmp_path, "pack", {"alpha": "A", "beta": "B"})
        result = FilesystemFreshnessInspector().assess(root)
        assert result.compilation_state == CompilationState.ABSENT

    def test_empty_pack_no_bytecode_is_absent(self, tmp_path):
        """Pack with index.md only, no items, no _bytecode/ → ABSENT."""
        root = write_pack(tmp_path, "pack", {})
        result = FilesystemFreshnessInspector().assess(root)
        assert result.compilation_state == CompilationState.ABSENT

    def test_all_mirrors_newer_is_clean(self, tmp_path):
        """All _bytecode/ mirrors newer than items → CLEAN."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A", "beta": "B"},
            bytecode={"alpha": "summary A", "beta": "summary B"},
        )
        # Age items, freshen mirrors
        age_file(root / "alpha.md")
        age_file(root / "beta.md")
        freshen_file(root / "_bytecode" / "alpha.md")
        freshen_file(root / "_bytecode" / "beta.md")

        result = FilesystemFreshnessInspector().assess(root)
        assert result.compilation_state == CompilationState.CLEAN

    def test_one_item_newer_than_mirror_is_dirty(self, tmp_path):
        """One item newer than its mirror → DIRTY, only that item dirty."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A", "beta": "B", "gamma": "C"},
            bytecode={"alpha": "sA", "beta": "sB", "gamma": "sC"},
        )
        # Make all items old, all mirrors fresh
        for name in ("alpha", "beta", "gamma"):
            age_file(root / f"{name}.md", seconds=20)
            freshen_file(root / "_bytecode" / f"{name}.md")
        # Make beta dirty: item newer than its mirror
        age_file(root / "_bytecode" / "beta.md", seconds=10)
        age_file(root / "beta.md", seconds=5)

        result = FilesystemFreshnessInspector().assess(root)
        assert result.compilation_state == CompilationState.DIRTY
        dirty = [i for i in result.items if i.state == "dirty"]
        assert len(dirty) == 1
        assert dirty[0].name == "beta"

    def test_new_item_with_no_mirror_is_dirty(self, tmp_path):
        """Item exists but no corresponding _bytecode/ mirror → DIRTY."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A", "beta": "B"},
            bytecode={"alpha": "sA"},  # no mirror for beta
        )
        age_file(root / "alpha.md")
        freshen_file(root / "_bytecode" / "alpha.md")

        result = FilesystemFreshnessInspector().assess(root)
        assert result.compilation_state == CompilationState.DIRTY
        absent = [i for i in result.items if i.state == "absent"]
        assert len(absent) == 1
        assert absent[0].name == "beta"

    def test_orphan_mirror_with_no_source_is_corrupt(self, tmp_path):
        """Mirror in _bytecode/ with no source item → CORRUPT."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA", "ghost": "orphan summary"},
        )
        age_file(root / "alpha.md")
        freshen_file(root / "_bytecode" / "alpha.md")
        freshen_file(root / "_bytecode" / "ghost.md")

        result = FilesystemFreshnessInspector().assess(root)
        assert result.compilation_state == CompilationState.CORRUPT
        orphans = [i for i in result.items if i.state == "orphan"]
        assert len(orphans) == 1
        assert orphans[0].name == "ghost"

    def test_edited_index_all_mirrors_fresh_is_clean(self, tmp_path):
        """index.md newer than everything, all mirrors fresh → CLEAN."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA"},
        )
        age_file(root / "alpha.md")
        freshen_file(root / "_bytecode" / "alpha.md")
        freshen_file(root / "index.md", seconds=10)

        result = FilesystemFreshnessInspector().assess(root)
        assert result.compilation_state == CompilationState.CLEAN

    def test_edited_summary_all_mirrors_fresh_is_clean(self, tmp_path):
        """summary.md newer than everything → CLEAN."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA"},
        )
        (root / "summary.md").write_text("Human summary")
        age_file(root / "alpha.md")
        freshen_file(root / "_bytecode" / "alpha.md")
        freshen_file(root / "summary.md", seconds=10)

        result = FilesystemFreshnessInspector().assess(root)
        assert result.compilation_state == CompilationState.CLEAN

    def test_mixed_dirty_and_orphan_is_corrupt(self, tmp_path):
        """Both stale items AND orphan mirrors → CORRUPT."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA", "ghost": "orphan"},
        )
        # alpha is dirty (item newer than mirror)
        age_file(root / "_bytecode" / "alpha.md", seconds=10)
        age_file(root / "alpha.md", seconds=5)

        result = FilesystemFreshnessInspector().assess(root)
        assert result.compilation_state == CompilationState.CORRUPT


# ---------------------------------------------------------------------------
# Phase 2: Nested freshness (deep traversal)
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestNestedFreshness:
    """Deep freshness traversal across nested packs."""

    def test_parent_clean_child_clean_is_clean(self, tmp_path):
        """Both levels have fresh mirrors → deep_state is CLEAN."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA", "child": "child summary"},
            children=[("child", {"one": "1"}, {"one": "s1"})],
        )
        # Age all items, freshen all mirrors.
        # Parent's child mirror must be newer than child's bytecode.
        age_file(root / "alpha.md", seconds=20)
        age_file(root / "child" / "one.md", seconds=20)
        freshen_file(root / "child" / "_bytecode" / "one.md", seconds=1)
        freshen_file(root / "_bytecode" / "alpha.md", seconds=2)
        freshen_file(root / "_bytecode" / "child.md", seconds=3)

        inspector = FilesystemFreshnessInspector()
        result = inspector.assess(root)
        assert result.compilation_state == CompilationState.CLEAN
        assert result.deep_state == CompilationState.CLEAN

    def test_parent_clean_child_dirty_is_dirty(self, tmp_path):
        """Parent's own items fresh, child has stale item → deep DIRTY."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA", "child": "child summary"},
            children=[("child", {"one": "1"}, {"one": "s1"})],
        )
        age_file(root / "alpha.md", seconds=20)
        freshen_file(root / "_bytecode" / "alpha.md", seconds=2)
        freshen_file(root / "_bytecode" / "child.md", seconds=3)
        # Child item is newer than its mirror
        age_file(root / "child" / "_bytecode" / "one.md", seconds=10)
        age_file(root / "child" / "one.md", seconds=5)

        inspector = FilesystemFreshnessInspector()
        result = inspector.assess(root)
        # Parent sees child is dirty → marks composite item as dirty
        assert result.compilation_state == CompilationState.DIRTY
        assert result.deep_state == CompilationState.DIRTY

    def test_three_level_cascade(self, tmp_path):
        """Grandchild dirty → child and parent deep_state DIRTY."""
        # Build bottom-up: grandchild, then child, then parent
        root = tmp_path / "pack"
        root.mkdir()
        (root / "index.md").write_text("---\nname: root\n---\n")
        (root / "alpha.md").write_text("A")

        child = root / "child"
        child.mkdir()
        (child / "index.md").write_text("---\nname: child\n---\n")
        (child / "one.md").write_text("1")

        grandchild = child / "grandchild"
        grandchild.mkdir()
        (grandchild / "index.md").write_text("---\nname: gc\n---\n")
        (grandchild / "deep.md").write_text("deep content")

        # Create bytecode at all levels
        for d, items, composites in [
            (root, ["alpha"], ["child"]),
            (child, ["one"], ["grandchild"]),
            (grandchild, ["deep"], []),
        ]:
            bc = d / "_bytecode"
            bc.mkdir()
            for name in items + composites:
                (bc / f"{name}.md").write_text(f"summary of {name}")

        # Age everything
        for d in (root, child, grandchild):
            for f in d.glob("*.md"):
                age_file(f, seconds=20)
            for f in (d / "_bytecode").glob("*.md"):
                freshen_file(f)

        # Make grandchild item dirty
        freshen_file(grandchild / "deep.md", seconds=5)
        age_file(grandchild / "_bytecode" / "deep.md")

        inspector = FilesystemFreshnessInspector()
        result = inspector.assess(root)

        # Find grandchild freshness
        child_freshness = result.children[0]
        gc_freshness = child_freshness.children[0]

        assert gc_freshness.deep_state == CompilationState.DIRTY
        assert child_freshness.deep_state == CompilationState.DIRTY
        assert result.deep_state == CompilationState.DIRTY

    def test_parent_summary_stale_after_child_bytecode_changes(self, tmp_path):
        """Child clean, parent's _bytecode/child.md older than child bytecode → DIRTY."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA", "child": "old child summary"},
            children=[("child", {"one": "1"}, {"one": "s1"})],
        )
        # All items old
        age_file(root / "alpha.md", seconds=20)
        age_file(root / "child" / "one.md", seconds=20)

        # Child bytecode is fresh (child was recently recompiled)
        freshen_file(root / "child" / "_bytecode" / "one.md", seconds=2)

        # Parent mirrors are older than child bytecode
        freshen_file(root / "_bytecode" / "alpha.md")
        age_file(root / "_bytecode" / "child.md", seconds=5)

        inspector = FilesystemFreshnessInspector()
        result = inspector.assess(root)
        assert result.compilation_state == CompilationState.DIRTY

    def test_child_corrupt_propagates(self, tmp_path):
        """Child has orphan mirrors → child CORRUPT → parent deep_state CORRUPT."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA", "child": "child summary"},
            children=[("child", {"one": "1"}, {"one": "s1", "ghost": "orphan"})],
        )
        age_file(root / "alpha.md")
        age_file(root / "child" / "one.md")
        freshen_file(root / "_bytecode" / "alpha.md")
        freshen_file(root / "_bytecode" / "child.md")
        freshen_file(root / "child" / "_bytecode" / "one.md")
        freshen_file(root / "child" / "_bytecode" / "ghost.md")

        inspector = FilesystemFreshnessInspector()
        result = inspector.assess(root)
        child_freshness = result.children[0]
        assert child_freshness.compilation_state == CompilationState.CORRUPT
        assert result.deep_state == CompilationState.CORRUPT


# ---------------------------------------------------------------------------
# Phase 3: Pack-and-wrap orchestration
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestPackAndWrap:
    """Pack-and-wrap compilation workflow."""

    def test_compile_absent_pack_creates_bytecode(self, tmp_path):
        """Pack with items, no _bytecode/ → compiles all, state CLEAN."""
        root = write_pack(tmp_path, "pack", {"alpha": "A", "beta": "B"})
        inspector = FilesystemFreshnessInspector()
        compiler = StubCompiler()

        result = pack_and_wrap(root, inspector, compiler)

        assert result.state_before == CompilationState.ABSENT
        assert result.state_after == CompilationState.CLEAN
        assert (root / "_bytecode").is_dir()
        assert set(result.compiled_items) == {"alpha", "beta"}
        assert len(compiler.calls) == 2

    def test_compile_dirty_pack_only_recompiles_dirty_items(self, tmp_path):
        """Only dirty items recompiled; clean mirrors untouched."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A", "beta": "B", "gamma": "C"},
            bytecode={"alpha": "sA", "beta": "sB", "gamma": "sC"},
        )
        # All items old, all mirrors fresh
        for name in ("alpha", "beta", "gamma"):
            age_file(root / f"{name}.md", seconds=20)
            freshen_file(root / "_bytecode" / f"{name}.md")
        # Make beta dirty by aging its mirror below the item
        age_file(root / "_bytecode" / "beta.md", seconds=10)
        age_file(root / "beta.md", seconds=5)

        inspector = FilesystemFreshnessInspector()
        compiler = StubCompiler()

        result = pack_and_wrap(root, inspector, compiler)

        assert result.state_before == CompilationState.DIRTY
        assert result.state_after == CompilationState.CLEAN
        assert result.compiled_items == ["beta"]
        assert len(compiler.calls) == 1

    def test_compile_clean_pack_is_noop(self, tmp_path):
        """All mirrors fresh → no compilation, state stays CLEAN."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA"},
        )
        age_file(root / "alpha.md")
        freshen_file(root / "_bytecode" / "alpha.md")

        inspector = FilesystemFreshnessInspector()
        compiler = StubCompiler()

        result = pack_and_wrap(root, inspector, compiler)

        assert result.state_before == CompilationState.CLEAN
        assert result.state_after == CompilationState.CLEAN
        assert result.compiled_items == []
        assert compiler.calls == []

    def test_idempotent_second_run_is_noop(self, tmp_path):
        """Second pack_and_wrap after compiling is a noop."""
        root = write_pack(tmp_path, "pack", {"alpha": "A", "beta": "B"})
        inspector = FilesystemFreshnessInspector()
        compiler = StubCompiler()

        # First run compiles everything
        pack_and_wrap(root, inspector, compiler)
        first_call_count = len(compiler.calls)

        # Second run should be noop
        result = pack_and_wrap(root, inspector, compiler)
        assert result.state_before == CompilationState.CLEAN
        assert result.state_after == CompilationState.CLEAN
        assert result.compiled_items == []
        assert len(compiler.calls) == first_call_count  # no new calls

    def test_corrupt_pack_deletes_orphans_before_compiling(self, tmp_path):
        """Orphan mirrors deleted, then dirty items compiled → CLEAN."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA", "ghost": "orphan"},
        )
        # alpha is dirty (item newer than mirror)
        age_file(root / "_bytecode" / "alpha.md", seconds=10)
        age_file(root / "alpha.md", seconds=5)

        inspector = FilesystemFreshnessInspector()
        compiler = StubCompiler()

        result = pack_and_wrap(root, inspector, compiler)

        assert result.state_before == CompilationState.CORRUPT
        assert result.state_after == CompilationState.CLEAN
        assert "ghost" in result.deleted_orphans
        assert "alpha" in result.compiled_items
        assert not (root / "_bytecode" / "ghost.md").exists()

    def test_deep_compiles_bottom_up(self, tmp_path):
        """Child compiled first, then parent."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            children=[("child", {"one": "1"}, None)],  # child has no bytecode
        )
        inspector = FilesystemFreshnessInspector()
        compiler = StubCompiler()

        result = pack_and_wrap(root, inspector, compiler, deep=True)

        assert result.state_after == CompilationState.CLEAN
        # Child items compiled before parent items
        call_stems = [c.stem for c in compiler.calls]
        child_idx = call_stems.index("one")
        # Parent items come after child items
        parent_items = [i for i, s in enumerate(call_stems) if s in ("alpha", "child")]
        assert all(child_idx < pi for pi in parent_items)

    def test_three_level_bottom_up_cascade(self, tmp_path):
        """Grandchild → child → parent compilation order."""
        root = tmp_path / "pack"
        root.mkdir()
        (root / "index.md").write_text("---\nname: root\n---\n")
        (root / "alpha.md").write_text("A")

        child = root / "child"
        child.mkdir()
        (child / "index.md").write_text("---\nname: child\n---\n")
        (child / "one.md").write_text("1")

        grandchild = child / "grandchild"
        grandchild.mkdir()
        (grandchild / "index.md").write_text("---\nname: gc\n---\n")
        (grandchild / "deep.md").write_text("deep content")

        inspector = FilesystemFreshnessInspector()
        compiler = StubCompiler()

        result = pack_and_wrap(root, inspector, compiler, deep=True)

        assert result.state_after == CompilationState.CLEAN
        call_stems = [c.stem for c in compiler.calls]
        # deep must come before one/grandchild, which must come before alpha/child
        deep_idx = call_stems.index("deep")
        one_idx = next(i for i, s in enumerate(call_stems) if s == "one")
        alpha_idx = next(i for i, s in enumerate(call_stems) if s == "alpha")
        assert deep_idx < one_idx < alpha_idx
