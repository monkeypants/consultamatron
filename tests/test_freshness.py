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

from bin.cli.dtos import PackStatusRequest
from bin.cli.usecases import PackStatusUseCase
from practice.exceptions import NotFoundError

from .conftest import StubCompiler, write_pack


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

    def test_all_hashes_match_is_clean(self, tmp_path):
        """All _bytecode/ mirrors have matching source hashes → CLEAN."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A", "beta": "B"},
            bytecode={"alpha": "summary A", "beta": "summary B"},
        )
        result = FilesystemFreshnessInspector().assess(root)
        assert result.compilation_state == CompilationState.CLEAN

    def test_one_item_changed_is_dirty(self, tmp_path):
        """One item modified after bytecode written → DIRTY, only that item dirty."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A", "beta": "B", "gamma": "C"},
            bytecode={"alpha": "sA", "beta": "sB", "gamma": "sC"},
        )
        # Modify beta's source — hash in bytecode no longer matches
        (root / "beta.md").write_text("B modified")

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
        result = FilesystemFreshnessInspector().assess(root)
        assert result.compilation_state == CompilationState.CORRUPT
        orphans = [i for i in result.items if i.state == "orphan"]
        assert len(orphans) == 1
        assert orphans[0].name == "ghost"

    def test_edited_index_all_hashes_match_is_clean(self, tmp_path):
        """index.md modified, all item hashes still match → CLEAN."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA"},
        )
        # Modify index — not a source item, should not affect freshness
        (root / "index.md").write_text("---\nname: updated\npurpose: New.\n---\n")

        result = FilesystemFreshnessInspector().assess(root)
        assert result.compilation_state == CompilationState.CLEAN

    def test_edited_summary_all_hashes_match_is_clean(self, tmp_path):
        """summary.md modified → CLEAN (not a source item)."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA"},
        )
        (root / "summary.md").write_text("Human summary")

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
        # Make alpha dirty by changing source
        (root / "alpha.md").write_text("A modified")

        result = FilesystemFreshnessInspector().assess(root)
        assert result.compilation_state == CompilationState.CORRUPT


# ---------------------------------------------------------------------------
# Phase 2: Nested freshness (deep traversal)
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestNestedFreshness:
    """Deep freshness traversal across nested packs."""

    def test_parent_clean_child_clean_is_clean(self, tmp_path):
        """Both levels have matching hashes → deep_state is CLEAN."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA", "child": "child summary"},
            children=[("child", {"one": "1"}, {"one": "s1"})],
        )
        inspector = FilesystemFreshnessInspector()
        result = inspector.assess(root)
        assert result.compilation_state == CompilationState.CLEAN
        assert result.deep_state == CompilationState.CLEAN

    def test_parent_clean_child_dirty_is_dirty(self, tmp_path):
        """Parent's own items match, child has changed item → deep DIRTY."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA", "child": "child summary"},
            children=[("child", {"one": "1"}, {"one": "s1"})],
        )
        # Make child item dirty
        (root / "child" / "one.md").write_text("1 modified")

        inspector = FilesystemFreshnessInspector()
        result = inspector.assess(root)
        assert result.compilation_state == CompilationState.DIRTY
        assert result.deep_state == CompilationState.DIRTY

    def test_three_level_cascade(self, tmp_path):
        """Grandchild dirty → child and parent deep_state DIRTY."""
        # Build a 3-level hierarchy with no bytecode
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

        # Compile the whole tree to establish a clean baseline
        inspector = FilesystemFreshnessInspector()
        compiler = StubCompiler()
        pack_and_wrap(root, inspector, compiler, deep=True)
        assert inspector.assess(root).deep_state == CompilationState.CLEAN

        # Now make grandchild dirty
        (grandchild / "deep.md").write_text("deep content MODIFIED")

        result = inspector.assess(root)
        child_freshness = result.children[0]
        gc_freshness = child_freshness.children[0]

        assert gc_freshness.deep_state == CompilationState.DIRTY
        assert child_freshness.deep_state == CompilationState.DIRTY
        assert result.deep_state == CompilationState.DIRTY

    def test_parent_summary_stale_after_child_bytecode_changes(self, tmp_path):
        """Child clean, parent's hash doesn't match child bytecode → DIRTY."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA", "child": "old child summary"},
            children=[("child", {"one": "1"}, {"one": "s1"})],
        )
        # Modify a child bytecode file — parent's composite hash now stale
        from practice.content_hash import hash_content
        from practice.frontmatter import format_frontmatter

        (root / "child" / "_bytecode" / "one.md").write_text(
            format_frontmatter({"source_hash": hash_content("1")}, "UPDATED summary")
        )

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
            children=[("child", {"one": "1"}, {"one": "s1"})],
        )
        # Add an orphan to child's bytecode
        (root / "child" / "_bytecode" / "ghost.md").write_text("orphan")

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
        # Make beta dirty by changing source
        (root / "beta.md").write_text("B modified")

        inspector = FilesystemFreshnessInspector()
        compiler = StubCompiler()

        result = pack_and_wrap(root, inspector, compiler)

        assert result.state_before == CompilationState.DIRTY
        assert result.state_after == CompilationState.CLEAN
        assert result.compiled_items == ["beta"]
        assert len(compiler.calls) == 1

    def test_compile_clean_pack_is_noop(self, tmp_path):
        """All hashes match → no compilation, state stays CLEAN."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA"},
        )
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
        # Make alpha dirty by changing source
        (root / "alpha.md").write_text("A modified")

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


# ---------------------------------------------------------------------------
# Phase 4: PackStatusUseCase
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestPackStatusUseCase:
    """CLI usecase for pack freshness inspection."""

    def test_status_returns_freshness_tree(self, tmp_path):
        """UseCase returns a response matching the assessed state."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A", "beta": "B"},
            bytecode={"alpha": "sA", "beta": "sB"},
        )
        inspector = FilesystemFreshnessInspector()
        usecase = PackStatusUseCase(inspector=inspector)
        resp = usecase.execute(PackStatusRequest(path=str(root)))

        assert resp.compilation_state == "clean"
        assert resp.deep_state == "clean"
        assert len(resp.items) == 2
        assert all(i.state == "clean" for i in resp.items)

    def test_status_missing_pack_raises(self, tmp_path):
        """Path with no index.md raises NotFoundError."""
        inspector = FilesystemFreshnessInspector()
        usecase = PackStatusUseCase(inspector=inspector)

        with pytest.raises(NotFoundError):
            usecase.execute(PackStatusRequest(path=str(tmp_path)))

    def test_status_nested_pack_includes_children(self, tmp_path):
        """Pack with child returns children with deep_state."""
        root = write_pack(
            tmp_path,
            "pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA", "child": "child summary"},
            children=[("child", {"one": "1"}, {"one": "s1"})],
        )
        inspector = FilesystemFreshnessInspector()
        usecase = PackStatusUseCase(inspector=inspector)
        resp = usecase.execute(PackStatusRequest(path=str(root)))

        assert resp.deep_state == "clean"
        assert len(resp.children) == 1
        assert resp.children[0].compilation_state == "clean"
