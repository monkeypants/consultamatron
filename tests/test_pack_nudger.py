"""Knowledge pack nudging — freshness hints for the operator.

Knowledge packs are compressed reference material that skills consume at
runtime. When a pack's bytecode drifts out of sync with its source
(dirty, corrupt, or absent), the nudger produces human-readable hints
so the operator knows to recompile before executing a skill.

Packs divide into two categories:

- **Platform packs** live under ``docs/``. They contain shared knowledge
  that every skill may depend on — architecture, conventions, onboarding.
  Platform packs are always checked.

- **BC packs** live inside bounded-context directories under ``commons/``,
  ``personal/``, or ``partnerships/``. Each BC owns knowledge specific to
  its skillsets. When the nudger receives a ``skillset_names`` scope
  (e.g. from an engagement status check), only the BCs that provide those
  skillsets are checked — irrelevant BC knowledge is not surfaced.

Three test phases:
  1. Frontmatter parsing — the identity mechanism for pack manifests
  2. Pack discovery — scanning source containers for packs with identity
  3. Nudge generation — freshness assessment and scoped filtering
"""

from __future__ import annotations

import pytest

from bin.cli.infrastructure.filesystem_freshness_inspector import (
    FilesystemFreshnessInspector,
)
from bin.cli.infrastructure.filesystem_knowledge_pack_repository import (
    FilesystemKnowledgePackRepository,
)
from bin.cli.infrastructure.pack_nudger import FilesystemPackNudger
from practice.frontmatter import parse_frontmatter

from .conftest import write_pack


# ---------------------------------------------------------------------------
# Phase 1: Frontmatter parsing — the identity mechanism for pack manifests
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestManifestFrontmatter:
    """Knowledge pack manifests declare identity through frontmatter.

    A pack exists to the system only when its index.md contains
    ``---``-delimited frontmatter with at least ``name`` and ``purpose``.
    The parser handles flat key-value pairs and the YAML ``>``
    folded-scalar continuation, without an external YAML dependency.
    """

    def test_parses_simple_key_value(self, tmp_path):
        """Flat key: value pairs extracted from ---delimited block."""
        index = tmp_path / "index.md"
        index.write_text("---\nname: my-pack\npurpose: Do things.\n---\nBody text.\n")
        fm = parse_frontmatter(index)
        assert fm == {"name": "my-pack", "purpose": "Do things."}

    def test_parses_folded_scalar(self, tmp_path):
        """YAML > (folded clip) joins indented lines, keeps trailing newline."""
        index = tmp_path / "index.md"
        index.write_text(
            "---\nname: my-pack\npurpose: >\n  Multi-line\n  purpose text.\n---\n"
        )
        fm = parse_frontmatter(index)
        assert fm["purpose"] == "Multi-line purpose text.\n"

    def test_no_frontmatter_returns_empty(self, tmp_path):
        """File without --- delimiters → pack has no identity."""
        index = tmp_path / "index.md"
        index.write_text("Just body text, no delimiters.\n")
        fm = parse_frontmatter(index)
        assert fm == {}

    def test_parses_nested_dict(self, tmp_path):
        """YAML nested mappings are preserved as dicts."""
        index = tmp_path / "index.md"
        index.write_text(
            "---\nname: my-skill\nmetadata:\n  author: monkeypants\n"
            "  version: '0.2'\n  freedom: high\n---\n"
        )
        fm = parse_frontmatter(index)
        assert fm["metadata"] == {
            "author": "monkeypants",
            "version": "0.2",
            "freedom": "high",
        }

    def test_parses_list_of_objects(self, tmp_path):
        """YAML list of objects is preserved."""
        index = tmp_path / "index.md"
        index.write_text(
            "---\nname: my-pack\npurpose: Test.\n"
            "actor_goals:\n  - actor: engineer\n    goal: build things\n---\n"
        )
        fm = parse_frontmatter(index)
        assert fm["actor_goals"] == [{"actor": "engineer", "goal": "build things"}]

    def test_parses_list_of_strings(self, tmp_path):
        """YAML list of strings is preserved."""
        index = tmp_path / "index.md"
        index.write_text(
            "---\nname: my-pack\npurpose: Test.\n"
            "triggers:\n  - first trigger\n  - second trigger\n---\n"
        )
        fm = parse_frontmatter(index)
        assert fm["triggers"] == ["first trigger", "second trigger"]

    def test_incomplete_frontmatter_returns_empty(self, tmp_path):
        """Single --- without closing delimiter → pack has no identity."""
        index = tmp_path / "index.md"
        index.write_text("---\nname: half\nNo closing delimiter.\n")
        fm = parse_frontmatter(index)
        assert fm == {}


# ---------------------------------------------------------------------------
# Phase 2: Pack discovery — scanning source containers
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestPackDiscovery:
    """The repository discovers knowledge packs across four source containers.

    Packs are found by scanning ``docs/``, ``commons/``, ``personal/``
    (when present), and each ``partnerships/{slug}/`` subdirectory for
    ``index.md`` files with both ``name`` and ``purpose`` frontmatter.
    A manifest missing either field is invisible to the system.
    """

    def _discover(self, repo_root):
        repo = FilesystemKnowledgePackRepository(repo_root)
        return [(pack.name, path) for pack, path in repo.packs_with_paths()]

    def test_discovers_pack_under_docs(self, tmp_path):
        """Platform pack in docs/ with name + purpose → discovered."""
        docs = tmp_path / "docs" / "my-pack"
        docs.mkdir(parents=True)
        (docs / "index.md").write_text("---\nname: my-pack\npurpose: Knowledge.\n---\n")
        packs = self._discover(tmp_path)
        assert len(packs) == 1
        assert packs[0] == ("my-pack", docs)

    def test_discovers_nested_pack(self, tmp_path):
        """Pack nested inside docs/sub/deep/ → still discovered by rglob."""
        nested = tmp_path / "docs" / "sub" / "deep"
        nested.mkdir(parents=True)
        (nested / "index.md").write_text(
            "---\nname: deep-pack\npurpose: Deep knowledge.\n---\n"
        )
        packs = self._discover(tmp_path)
        assert ("deep-pack", nested) in packs

    def test_discovers_pack_under_commons(self, tmp_path):
        """BC pack in commons/my_bc/docs/ → discovered."""
        bc_docs = tmp_path / "commons" / "my_bc" / "docs"
        bc_docs.mkdir(parents=True)
        (bc_docs / "index.md").write_text(
            "---\nname: bc-pack\npurpose: BC knowledge.\n---\n"
        )
        packs = self._discover(tmp_path)
        assert ("bc-pack", bc_docs) in packs

    def test_ignores_index_without_purpose(self, tmp_path):
        """Manifest with name but no purpose → pack is invisible."""
        docs = tmp_path / "docs" / "half"
        docs.mkdir(parents=True)
        (docs / "index.md").write_text("---\nname: half\n---\n")
        packs = self._discover(tmp_path)
        assert packs == []

    def test_ignores_index_without_name(self, tmp_path):
        """Manifest with purpose but no name → pack is invisible."""
        docs = tmp_path / "docs" / "half"
        docs.mkdir(parents=True)
        (docs / "index.md").write_text("---\npurpose: No name.\n---\n")
        packs = self._discover(tmp_path)
        assert packs == []

    def test_discovers_under_personal(self, tmp_path):
        """Pack in personal/ source container → discovered."""
        personal = tmp_path / "personal" / "my-pack"
        personal.mkdir(parents=True)
        (personal / "index.md").write_text(
            "---\nname: personal-pack\npurpose: Personal knowledge.\n---\n"
        )
        packs = self._discover(tmp_path)
        assert ("personal-pack", personal) in packs

    def test_discovers_under_partnerships(self, tmp_path):
        """Pack in partnerships/acme/ source container → discovered."""
        partner = tmp_path / "partnerships" / "acme" / "docs"
        partner.mkdir(parents=True)
        (partner / "index.md").write_text(
            "---\nname: acme-pack\npurpose: Acme knowledge.\n---\n"
        )
        packs = self._discover(tmp_path)
        assert ("acme-pack", partner) in packs

    def test_skips_missing_dirs(self, tmp_path):
        """Absent personal/ and partnerships/ directories → no error."""
        (tmp_path / "docs").mkdir()
        packs = self._discover(tmp_path)
        assert packs == []


# ---------------------------------------------------------------------------
# Phase 3: Nudge generation — freshness assessment and scoped filtering
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestFilesystemPackNudger:
    """The nudger checks knowledge pack freshness and produces operator hints.

    When bytecode is stale (dirty), orphaned (corrupt), or missing
    (absent), the nudger returns human-readable strings telling the
    operator which pack needs recompilation and the command to run.

    When ``skillset_names`` is provided (e.g. from an engagement status
    check), the nudger scopes its work: platform packs under ``docs/``
    are always checked because they're shared infrastructure, but BC
    packs are only checked when their bounded context provides one of
    the listed skillsets. This avoids surfacing irrelevant nudges when
    the operator is focused on a specific engagement.
    """

    def _make_nudger(self, repo_root, *, skillset_bc_dirs=None):
        inspector = FilesystemFreshnessInspector()
        knowledge_packs = FilesystemKnowledgePackRepository(repo_root)
        return FilesystemPackNudger(
            repo_root, inspector, skillset_bc_dirs, knowledge_packs=knowledge_packs
        )

    # -- Unscoped checks (no skillset filter) --

    def test_clean_pack_no_nudges(self, tmp_path):
        """All bytecode hashes match → no nudges emitted."""
        docs = tmp_path / "docs"
        write_pack(
            docs,
            "my-pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA"},
            manifest={"name": "my-pack", "purpose": "Test."},
        )

        nudger = self._make_nudger(tmp_path)
        assert nudger.check() == []

    def test_dirty_pack_produces_nudge(self, tmp_path):
        """Stale bytecode in a known pack → operator gets a recompilation hint."""
        docs = tmp_path / "docs"
        pack_root = write_pack(
            docs,
            "my-pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA"},
            manifest={"name": "my-pack", "purpose": "Test."},
        )
        # Make alpha dirty by changing source
        (pack_root / "alpha.md").write_text("A modified")

        nudger = self._make_nudger(tmp_path)
        nudges = nudger.check()
        assert len(nudges) == 1
        assert "my-pack" in nudges[0]

    def test_absent_pack_produces_nudge(self, tmp_path):
        """Pack with no _bytecode/ directory → nudge about missing compilation."""
        docs = tmp_path / "docs"
        write_pack(
            docs,
            "my-pack",
            {"alpha": "A"},
            manifest={"name": "my-pack", "purpose": "Test."},
        )

        nudger = self._make_nudger(tmp_path)
        nudges = nudger.check()
        assert len(nudges) == 1
        assert "no compiled bytecode" in nudges[0]

    def test_corrupt_pack_produces_nudge(self, tmp_path):
        """Orphan bytecode mirrors with no source item → corruption nudge."""
        docs = tmp_path / "docs"
        write_pack(
            docs,
            "my-pack",
            {"alpha": "A"},
            bytecode={"alpha": "sA", "ghost": "orphan"},
            manifest={"name": "my-pack", "purpose": "Test."},
        )

        nudger = self._make_nudger(tmp_path)
        nudges = nudger.check()
        assert len(nudges) == 1
        assert "orphan" in nudges[0]

    def test_multiple_packs_multiple_nudges(self, tmp_path):
        """Each non-clean pack produces exactly one nudge string."""
        docs = tmp_path / "docs"
        for pack_name in ("pack-a", "pack-b"):
            write_pack(
                docs,
                pack_name,
                {"item": "content"},
                manifest={"name": pack_name, "purpose": "Test."},
            )

        nudger = self._make_nudger(tmp_path)
        nudges = nudger.check()
        assert len(nudges) == 2

    def test_nudge_contains_pack_name_and_path(self, tmp_path):
        """Nudge string includes the pack name, relative path, and remediation command."""
        docs = tmp_path / "docs"
        write_pack(
            docs,
            "my-pack",
            {"alpha": "A"},
            manifest={"name": "my-pack", "purpose": "Test."},
        )

        nudger = self._make_nudger(tmp_path)
        nudges = nudger.check()
        assert len(nudges) == 1
        assert "my-pack" in nudges[0]
        assert "docs/my-pack" in nudges[0]
        assert "practice pack status" in nudges[0]

    def test_none_skillset_scope_checks_all_packs(self, tmp_path):
        """Explicit None scope is equivalent to no scope — all packs checked."""
        docs = tmp_path / "docs"
        write_pack(
            docs,
            "my-pack",
            {"alpha": "A"},
            manifest={"name": "my-pack", "purpose": "Test."},
        )

        nudger = self._make_nudger(tmp_path)
        nudges_default = nudger.check()
        nudges_none = nudger.check(skillset_names=None)
        assert nudges_default == nudges_none

    # -- Skillset-scoped checks (engagement context) --

    def test_platform_knowledge_checked_regardless_of_skillset_scope(self, tmp_path):
        """docs/ packs are shared infrastructure — always checked, even with a scope."""
        docs = tmp_path / "docs"
        write_pack(
            docs,
            "platform-pack",
            {"alpha": "A"},
            manifest={"name": "platform-pack", "purpose": "Platform."},
        )

        bc_dir = tmp_path / "commons" / "other_bc"
        bc_dir.mkdir(parents=True)

        nudger = self._make_nudger(
            tmp_path, skillset_bc_dirs={"other-skillset": bc_dir}
        )
        nudges = nudger.check(skillset_names=["other-skillset"])
        assert len(nudges) == 1
        assert "platform-pack" in nudges[0]

    def test_skillset_scoped_check_includes_relevant_bc_knowledge(self, tmp_path):
        """BC pack whose skillset is in scope → nudge surfaced."""
        bc_dir = tmp_path / "commons" / "my_bc"
        bc_docs = bc_dir / "docs"
        write_pack(
            bc_docs,
            "bc-pack",
            {"item": "content"},
            manifest={"name": "bc-pack", "purpose": "BC knowledge."},
        )

        nudger = self._make_nudger(tmp_path, skillset_bc_dirs={"my-skillset": bc_dir})
        nudges = nudger.check(skillset_names=["my-skillset"])
        bc_nudges = [n for n in nudges if "bc-pack" in n]
        assert len(bc_nudges) == 1

    def test_skillset_scoped_check_skips_unrelated_bc_knowledge(self, tmp_path):
        """BC pack whose skillset is not in scope → no nudge."""
        excluded_bc = tmp_path / "commons" / "excluded_bc"
        excluded_docs = excluded_bc / "docs"
        write_pack(
            excluded_docs,
            "excluded-pack",
            {"item": "content"},
            manifest={"name": "excluded-pack", "purpose": "Excluded."},
        )

        allowed_bc = tmp_path / "commons" / "allowed_bc"
        allowed_bc.mkdir(parents=True)

        nudger = self._make_nudger(
            tmp_path, skillset_bc_dirs={"allowed-skillset": allowed_bc}
        )
        nudges = nudger.check(skillset_names=["allowed-skillset"])
        excluded_nudges = [n for n in nudges if "excluded-pack" in n]
        assert excluded_nudges == []

    def test_unknown_skillset_falls_back_to_platform_knowledge(self, tmp_path):
        """Skillset name not in the mapping → only platform packs nudged."""
        docs = tmp_path / "docs"
        write_pack(
            docs,
            "platform-pack",
            {"alpha": "A"},
            manifest={"name": "platform-pack", "purpose": "Platform."},
        )

        bc_dir = tmp_path / "commons" / "my_bc"
        bc_docs = bc_dir / "docs"
        write_pack(
            bc_docs,
            "bc-pack",
            {"item": "content"},
            manifest={"name": "bc-pack", "purpose": "BC knowledge."},
        )

        nudger = self._make_nudger(tmp_path, skillset_bc_dirs={"my-skillset": bc_dir})
        nudges = nudger.check(skillset_names=["nonexistent-skillset"])
        assert len(nudges) == 1
        assert "platform-pack" in nudges[0]

    def test_multiple_skillsets_include_all_relevant_bc_knowledge(self, tmp_path):
        """Multiple skillsets in scope → packs from all their BCs are checked."""
        bc_a = tmp_path / "commons" / "bc_a"
        bc_a_docs = bc_a / "docs"
        write_pack(
            bc_a_docs,
            "pack-a",
            {"item": "content"},
            manifest={"name": "pack-a", "purpose": "BC A knowledge."},
        )

        bc_b = tmp_path / "commons" / "bc_b"
        bc_b_docs = bc_b / "docs"
        write_pack(
            bc_b_docs,
            "pack-b",
            {"item": "content"},
            manifest={"name": "pack-b", "purpose": "BC B knowledge."},
        )

        nudger = self._make_nudger(
            tmp_path,
            skillset_bc_dirs={"skillset-a": bc_a, "skillset-b": bc_b},
        )
        nudges = nudger.check(skillset_names=["skillset-a", "skillset-b"])
        names = {n.split("'")[1] for n in nudges}
        assert "pack-a" in names
        assert "pack-b" in names

    def test_empty_skillset_scope_checks_only_platform_knowledge(self, tmp_path):
        """Empty scope list → only platform packs, no BC packs."""
        docs = tmp_path / "docs"
        write_pack(
            docs,
            "platform-pack",
            {"alpha": "A"},
            manifest={"name": "platform-pack", "purpose": "Platform."},
        )

        bc_dir = tmp_path / "commons" / "my_bc"
        bc_docs = bc_dir / "docs"
        write_pack(
            bc_docs,
            "bc-pack",
            {"item": "content"},
            manifest={"name": "bc-pack", "purpose": "BC knowledge."},
        )

        nudger = self._make_nudger(tmp_path, skillset_bc_dirs={"my-skillset": bc_dir})
        nudges = nudger.check(skillset_names=[])
        assert len(nudges) == 1
        assert "platform-pack" in nudges[0]
