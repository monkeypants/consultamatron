"""Tests for partnership discovery and composite skillset aggregation.

Covers FilesystemSourceRepository (source discovery from filesystem)
and CompositeSkillsetRepository (merging commons + partnership skillsets).
"""

from __future__ import annotations

import json

import pytest

from bin.cli.infrastructure.composite_skillset_repository import (
    CompositeSkillsetRepository,
)
from bin.cli.infrastructure.filesystem_source_repository import (
    FilesystemSourceRepository,
)
from practice.entities import SourceType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_partnership(repo_root, slug, skillsets):
    """Create a partnership directory with a skillsets/index.json."""
    index = repo_root / "partners" / slug / "skillsets" / "index.json"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(json.dumps(skillsets, indent=2) + "\n")


def _make_skillset_json(name, display_name="Test Skillset", description="A test."):
    """Build a Skillset-shaped dict for writing to partnership JSON."""
    return {
        "name": name,
        "display_name": display_name,
        "description": description,
        "pipeline": [
            {
                "order": 1,
                "skill": f"{name}-start",
                "prerequisite_gate": "resources/index.md",
                "produces_gate": "brief.agreed.md",
                "description": "Stage 1: Brief agreed",
            },
        ],
        "slug_pattern": f"{name}-{{n}}",
    }


class StubSkillsetRepo:
    """Minimal SkillsetRepository for test isolation."""

    def __init__(self, skillsets):
        self._skillsets = skillsets

    def get(self, name):
        for s in self._skillsets:
            if s.name == name:
                return s
        return None

    def list_all(self):
        return list(self._skillsets)


@pytest.fixture
def commons_repo():
    """A stub SkillsetRepository with two commons skillsets."""
    from tests.conftest import make_skillset

    return StubSkillsetRepo(
        [
            make_skillset(name="wardley-mapping"),
            make_skillset(name="business-model-canvas", slug_pattern="bmc-{n}"),
        ]
    )


# ---------------------------------------------------------------------------
# FilesystemSourceRepository
# ---------------------------------------------------------------------------


class TestFilesystemSourceEmpty:
    """No partnerships directory at all."""

    def test_list_returns_only_commons(self, tmp_path, commons_repo):
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        sources = repo.list_all()
        assert len(sources) == 1
        assert sources[0].slug == "commons"
        assert sources[0].source_type == SourceType.COMMONS

    def test_get_commons(self, tmp_path, commons_repo):
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        source = repo.get("commons")
        assert source is not None
        assert source.slug == "commons"
        assert "wardley-mapping" in source.skillset_names

    def test_get_unknown_returns_none(self, tmp_path, commons_repo):
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert repo.get("nonexistent") is None


class TestFilesystemSourceSinglePartnership:
    """One partnership directory with skillsets."""

    def test_list_includes_partnership(self, tmp_path, commons_repo):
        _write_partnership(
            tmp_path, "acme-corp", [_make_skillset_json("acme-analysis")]
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        sources = repo.list_all()
        assert len(sources) == 2
        slugs = [s.slug for s in sources]
        assert "commons" in slugs
        assert "acme-corp" in slugs

    def test_get_partnership(self, tmp_path, commons_repo):
        _write_partnership(
            tmp_path, "acme-corp", [_make_skillset_json("acme-analysis")]
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        source = repo.get("acme-corp")
        assert source is not None
        assert source.source_type == SourceType.PARTNERSHIP
        assert source.skillset_names == ["acme-analysis"]

    def test_provenance_commons(self, tmp_path, commons_repo):
        _write_partnership(
            tmp_path, "acme-corp", [_make_skillset_json("acme-analysis")]
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert repo.skillset_source("wardley-mapping") == "commons"

    def test_provenance_partnership(self, tmp_path, commons_repo):
        _write_partnership(
            tmp_path, "acme-corp", [_make_skillset_json("acme-analysis")]
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert repo.skillset_source("acme-analysis") == "acme-corp"

    def test_provenance_unknown(self, tmp_path, commons_repo):
        _write_partnership(
            tmp_path, "acme-corp", [_make_skillset_json("acme-analysis")]
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert repo.skillset_source("nonexistent") is None


class TestFilesystemSourceMultiplePartnerships:
    """Multiple partnership directories."""

    def test_list_includes_all(self, tmp_path, commons_repo):
        _write_partnership(
            tmp_path, "acme-corp", [_make_skillset_json("acme-analysis")]
        )
        _write_partnership(
            tmp_path,
            "beta-inc",
            [
                _make_skillset_json("beta-audit"),
                _make_skillset_json("beta-compliance"),
            ],
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        sources = repo.list_all()
        assert len(sources) == 3
        slugs = [s.slug for s in sources]
        assert set(slugs) == {"commons", "acme-corp", "beta-inc"}

    def test_partnership_multiple_skillsets(self, tmp_path, commons_repo):
        _write_partnership(
            tmp_path,
            "beta-inc",
            [
                _make_skillset_json("beta-audit"),
                _make_skillset_json("beta-compliance"),
            ],
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        source = repo.get("beta-inc")
        assert source is not None
        assert source.skillset_names == ["beta-audit", "beta-compliance"]

    def test_provenance_resolves_correct_source(self, tmp_path, commons_repo):
        _write_partnership(
            tmp_path, "acme-corp", [_make_skillset_json("acme-analysis")]
        )
        _write_partnership(tmp_path, "beta-inc", [_make_skillset_json("beta-audit")])
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert repo.skillset_source("acme-analysis") == "acme-corp"
        assert repo.skillset_source("beta-audit") == "beta-inc"


class TestFilesystemSourceIgnoresInvalid:
    """Directories without skillsets/index.json are skipped."""

    def test_dir_without_index_ignored(self, tmp_path, commons_repo):
        (tmp_path / "partners" / "empty-partner").mkdir(parents=True)
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert len(repo.list_all()) == 1

    def test_file_in_partnerships_ignored(self, tmp_path, commons_repo):
        partnerships_dir = tmp_path / "partners"
        partnerships_dir.mkdir(parents=True)
        (partnerships_dir / "README.md").write_text("Not a partnership")
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert len(repo.list_all()) == 1


# ---------------------------------------------------------------------------
# CompositeSkillsetRepository
# ---------------------------------------------------------------------------


class TestCompositeNoPartnerships:
    """Composite with no partnership directories returns only commons."""

    def test_list_returns_commons(self, tmp_path, commons_repo):
        repo = CompositeSkillsetRepository(commons_repo, tmp_path)
        skillsets = repo.list_all()
        names = [s.name for s in skillsets]
        assert "wardley-mapping" in names
        assert "business-model-canvas" in names

    def test_get_commons_skillset(self, tmp_path, commons_repo):
        repo = CompositeSkillsetRepository(commons_repo, tmp_path)
        s = repo.get("wardley-mapping")
        assert s is not None
        assert s.name == "wardley-mapping"

    def test_get_unknown_returns_none(self, tmp_path, commons_repo):
        repo = CompositeSkillsetRepository(commons_repo, tmp_path)
        assert repo.get("nonexistent") is None


class TestCompositeMergesPartnerships:
    """Composite merges commons and partnership skillsets."""

    def test_list_includes_partnership_skillsets(self, tmp_path, commons_repo):
        _write_partnership(
            tmp_path, "acme-corp", [_make_skillset_json("acme-analysis")]
        )
        repo = CompositeSkillsetRepository(commons_repo, tmp_path)
        names = [s.name for s in repo.list_all()]
        assert "wardley-mapping" in names
        assert "acme-analysis" in names

    def test_get_partnership_skillset(self, tmp_path, commons_repo):
        _write_partnership(
            tmp_path, "acme-corp", [_make_skillset_json("acme-analysis")]
        )
        repo = CompositeSkillsetRepository(commons_repo, tmp_path)
        s = repo.get("acme-analysis")
        assert s is not None
        assert s.name == "acme-analysis"
        assert len(s.pipeline) == 1

    def test_commons_takes_precedence(self, tmp_path, commons_repo):
        """If a partnership declares the same name, commons wins."""
        _write_partnership(
            tmp_path,
            "acme-corp",
            [_make_skillset_json("wardley-mapping", description="Duplicate")],
        )
        repo = CompositeSkillsetRepository(commons_repo, tmp_path)
        s = repo.get("wardley-mapping")
        assert s is not None
        assert s.description != "Duplicate"

    def test_multiple_partnerships_merged(self, tmp_path, commons_repo):
        _write_partnership(
            tmp_path, "acme-corp", [_make_skillset_json("acme-analysis")]
        )
        _write_partnership(tmp_path, "beta-inc", [_make_skillset_json("beta-audit")])
        repo = CompositeSkillsetRepository(commons_repo, tmp_path)
        names = [s.name for s in repo.list_all()]
        assert "acme-analysis" in names
        assert "beta-audit" in names
