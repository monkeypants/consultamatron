"""Tests for source discovery across all source containers.

Covers FilesystemSourceRepository (source discovery from filesystem)
and CodeSkillsetRepository (unified pipeline aggregation from commons,
personal, and partnership BC packages).
"""

from __future__ import annotations

import pytest

from practice.bc_discovery import collect_pipelines
from bin.cli.infrastructure.filesystem_source_repository import (
    FilesystemSourceRepository,
)
from practice.entities import SourceType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_bc_package(parent_dir, pkg_name, pipeline_defs):
    """Create a BC package directory with __init__.py exporting PIPELINES.

    pipeline_defs is a list of dicts like:
        [{"name": "acme-analysis", "display_name": "Acme Analysis", ...}]
    """
    pkg_dir = parent_dir / pkg_name
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # Build the Python source for __init__.py
    lines = [
        "from practice.discovery import PipelineStage",
        "from practice.entities import Pipeline",
        "",
        "PIPELINES = [",
    ]
    for sd in pipeline_defs:
        stages_src = ""
        if sd.get("stages"):
            stages = []
            for stage in sd["stages"]:
                stages.append(
                    f"        PipelineStage("
                    f"order={stage['order']}, "
                    f"skill={stage['skill']!r}, "
                    f"prerequisite_gate={stage['prerequisite_gate']!r}, "
                    f"produces_gate={stage['produces_gate']!r}, "
                    f"description={stage['description']!r})"
                )
            stages_src = ",\n".join(stages)

        lines.append("    Pipeline(")
        lines.append(f"        name={sd['name']!r},")
        lines.append(f"        display_name={sd.get('display_name', 'Test')!r},")
        lines.append(f"        description={sd.get('description', 'A test.')!r},")
        lines.append(
            f"        slug_pattern={sd.get('slug_pattern', sd['name'] + '-{n}')!r},"
        )
        if stages_src:
            lines.append("        stages=[")
            lines.append(stages_src)
            lines.append("        ],")
        lines.append("    ),")
    lines.append("]")

    (pkg_dir / "__init__.py").write_text("\n".join(lines) + "\n")


def _make_pipeline_def(name, display_name="Test Pipeline", description="A test."):
    """Build a pipeline definition dict for _write_bc_package."""
    return {
        "name": name,
        "display_name": display_name,
        "description": description,
        "slug_pattern": f"{name}-{{n}}",
        "stages": [
            {
                "order": 1,
                "skill": f"{name}-start",
                "prerequisite_gate": "resources/index.md",
                "produces_gate": "brief.agreed.md",
                "description": "Stage 1: Brief agreed",
            },
        ],
    }


class StubSkillsetRepo:
    """Minimal SkillsetRepository for test isolation."""

    def __init__(self, pipelines):
        self._pipelines = pipelines

    def get(self, name):
        for p in self._pipelines:
            if p.name == name:
                return p
        return None

    def list_all(self):
        return list(self._pipelines)


@pytest.fixture
def commons_repo():
    """A stub SkillsetRepository with two commons pipelines."""
    from tests.conftest import make_pipeline

    return StubSkillsetRepo(
        [
            make_pipeline(name="wardley-mapping"),
            make_pipeline(name="business-model-canvas", slug_pattern="bmc-{n}"),
        ]
    )


# ---------------------------------------------------------------------------
# FilesystemSourceRepository — no extra sources
# ---------------------------------------------------------------------------


class TestFilesystemSourceEmpty:
    """No partnerships or personal directory at all."""

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


# ---------------------------------------------------------------------------
# FilesystemSourceRepository — personal source
# ---------------------------------------------------------------------------


class TestFilesystemSourcePersonal:
    """Personal BC packages in personal/skillsets/."""

    def test_personal_source_discovered(self, tmp_path, commons_repo):
        _write_bc_package(
            tmp_path / "personal" / "skillsets",
            "my_analysis",
            [_make_pipeline_def("my-analysis")],
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        source = repo.get("personal")
        assert source is not None
        assert source.source_type == SourceType.PERSONAL
        assert "my-analysis" in source.skillset_names

    def test_personal_included_in_list(self, tmp_path, commons_repo):
        _write_bc_package(
            tmp_path / "personal" / "skillsets",
            "my_analysis",
            [_make_pipeline_def("my-analysis")],
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        slugs = [s.slug for s in repo.list_all()]
        assert "personal" in slugs

    def test_personal_provenance(self, tmp_path, commons_repo):
        _write_bc_package(
            tmp_path / "personal" / "skillsets",
            "my_analysis",
            [_make_pipeline_def("my-analysis")],
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert repo.skillset_source("my-analysis") == "personal"

    def test_empty_personal_not_in_list(self, tmp_path, commons_repo):
        (tmp_path / "personal").mkdir()
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        slugs = [s.slug for s in repo.list_all()]
        assert "personal" not in slugs


# ---------------------------------------------------------------------------
# FilesystemSourceRepository — partnership sources
# ---------------------------------------------------------------------------


class TestFilesystemSourceSinglePartnership:
    """One partnership directory with BC packages."""

    def test_list_includes_partnership(self, tmp_path, commons_repo):
        _write_bc_package(
            tmp_path / "partnerships" / "acme-corp" / "skillsets",
            "acme_analysis",
            [_make_pipeline_def("acme-analysis")],
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        sources = repo.list_all()
        slugs = [s.slug for s in sources]
        assert "commons" in slugs
        assert "acme-corp" in slugs

    def test_get_partnership(self, tmp_path, commons_repo):
        _write_bc_package(
            tmp_path / "partnerships" / "acme-corp" / "skillsets",
            "acme_analysis",
            [_make_pipeline_def("acme-analysis")],
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        source = repo.get("acme-corp")
        assert source is not None
        assert source.source_type == SourceType.PARTNERSHIP
        assert source.skillset_names == ["acme-analysis"]

    def test_provenance_commons(self, tmp_path, commons_repo):
        _write_bc_package(
            tmp_path / "partnerships" / "acme-corp" / "skillsets",
            "acme_analysis",
            [_make_pipeline_def("acme-analysis")],
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert repo.skillset_source("wardley-mapping") == "commons"

    def test_provenance_partnership(self, tmp_path, commons_repo):
        _write_bc_package(
            tmp_path / "partnerships" / "acme-corp" / "skillsets",
            "acme_analysis",
            [_make_pipeline_def("acme-analysis")],
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert repo.skillset_source("acme-analysis") == "acme-corp"

    def test_provenance_unknown(self, tmp_path, commons_repo):
        _write_bc_package(
            tmp_path / "partnerships" / "acme-corp" / "skillsets",
            "acme_analysis",
            [_make_pipeline_def("acme-analysis")],
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert repo.skillset_source("nonexistent") is None


class TestFilesystemSourceMultiplePartnerships:
    """Multiple partnership directories."""

    def test_list_includes_all(self, tmp_path, commons_repo):
        _write_bc_package(
            tmp_path / "partnerships" / "acme-corp" / "skillsets",
            "acme_analysis",
            [_make_pipeline_def("acme-analysis")],
        )
        _write_bc_package(
            tmp_path / "partnerships" / "beta-inc" / "skillsets",
            "beta_audit",
            [
                _make_pipeline_def("beta-audit"),
                _make_pipeline_def("beta-compliance"),
            ],
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        sources = repo.list_all()
        slugs = [s.slug for s in sources]
        assert set(slugs) >= {"commons", "acme-corp", "beta-inc"}

    def test_partnership_multiple_skillsets(self, tmp_path, commons_repo):
        _write_bc_package(
            tmp_path / "partnerships" / "beta-inc" / "skillsets",
            "beta_audit",
            [_make_pipeline_def("beta-audit")],
        )
        _write_bc_package(
            tmp_path / "partnerships" / "beta-inc" / "skillsets",
            "beta_compliance",
            [_make_pipeline_def("beta-compliance")],
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        source = repo.get("beta-inc")
        assert source is not None
        assert source.skillset_names == ["beta-audit", "beta-compliance"]

    def test_provenance_resolves_correct_source(self, tmp_path, commons_repo):
        _write_bc_package(
            tmp_path / "partnerships" / "acme-corp" / "skillsets",
            "acme_analysis",
            [_make_pipeline_def("acme-analysis")],
        )
        _write_bc_package(
            tmp_path / "partnerships" / "beta-inc" / "skillsets",
            "beta_audit",
            [_make_pipeline_def("beta-audit")],
        )
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert repo.skillset_source("acme-analysis") == "acme-corp"
        assert repo.skillset_source("beta-audit") == "beta-inc"


class TestFilesystemSourceIgnoresInvalid:
    """Directories without BC packages are skipped."""

    def test_dir_without_init_ignored(self, tmp_path, commons_repo):
        (tmp_path / "partnerships" / "empty-partner").mkdir(parents=True)
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert len(repo.list_all()) == 1

    def test_file_in_partnerships_ignored(self, tmp_path, commons_repo):
        partnerships_dir = tmp_path / "partnerships"
        partnerships_dir.mkdir(parents=True)
        (partnerships_dir / "README.md").write_text("Not a partnership")
        repo = FilesystemSourceRepository(tmp_path, commons_repo)
        assert len(repo.list_all()) == 1


# ---------------------------------------------------------------------------
# collect_pipelines — BC package scanning
# ---------------------------------------------------------------------------


class TestCollectPipelines:
    """Unit tests for the BC package scanner."""

    def test_empty_directory(self, tmp_path):
        assert collect_pipelines(tmp_path) == []

    def test_nonexistent_directory(self, tmp_path):
        assert collect_pipelines(tmp_path / "nope") == []

    def test_discovers_bc_package(self, tmp_path):
        _write_bc_package(tmp_path, "test_pkg", [_make_pipeline_def("test-pipeline")])
        pipelines = collect_pipelines(tmp_path)
        assert len(pipelines) == 1
        assert pipelines[0].name == "test-pipeline"

    def test_ignores_dirs_without_init(self, tmp_path):
        (tmp_path / "no_init").mkdir()
        assert collect_pipelines(tmp_path) == []

    def test_multiple_packages(self, tmp_path):
        _write_bc_package(tmp_path, "pkg_a", [_make_pipeline_def("alpha")])
        _write_bc_package(tmp_path, "pkg_b", [_make_pipeline_def("beta")])
        pipelines = collect_pipelines(tmp_path)
        names = [p.name for p in pipelines]
        assert "alpha" in names
        assert "beta" in names


class TestDiscoveryFindsPipelines:
    """BC discovery finds PIPELINES attribute from modules."""

    def test_discovers_pipelines_attribute(self, tmp_path):
        _write_bc_package(tmp_path, "test_pkg", [_make_pipeline_def("test-pipeline")])
        pipelines = collect_pipelines(tmp_path)
        assert len(pipelines) == 1
        assert pipelines[0].name == "test-pipeline"
        assert pipelines[0].slug_pattern == "test-pipeline-{n}"


# ---------------------------------------------------------------------------
# collect_skillset_objects — Skillset-level BC package scanning
# ---------------------------------------------------------------------------


class TestCollectSkillsetObjects:
    """collect_skillset_objects returns Skillset entities from BC modules."""

    def test_collect_skillsets_from_SKILLSET_attr(self, tmp_path):
        """Module with SKILLSET attribute yields that Skillset directly."""
        from practice.bc_discovery import collect_skillset_objects

        pkg_dir = tmp_path / "skillset_pkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text(
            "from practice.entities import Pipeline, Skillset\n"
            "SKILLSET = Skillset(\n"
            "    name='test-ss',\n"
            "    display_name='Test',\n"
            "    description='A test.',\n"
            "    pipelines=[Pipeline(\n"
            "        name='create',\n"
            "        display_name='Create',\n"
            "        description='Create something.',\n"
            "        slug_pattern='test-{n}',\n"
            "    )],\n"
            ")\n"
        )
        skillsets = collect_skillset_objects(tmp_path)
        assert len(skillsets) == 1
        assert skillsets[0].name == "test-ss"
        assert len(skillsets[0].pipelines) == 1
        assert skillsets[0].pipelines[0].name == "create"

    def test_collect_skillsets_wraps_PIPELINES(self, tmp_path):
        """Module with only PIPELINES attribute gets auto-wrapped in Skillset."""
        from practice.bc_discovery import collect_skillset_objects

        _write_bc_package(
            tmp_path, "legacy_pkg", [_make_pipeline_def("legacy-pipeline")]
        )
        skillsets = collect_skillset_objects(tmp_path)
        assert len(skillsets) == 1
        assert isinstance(skillsets[0].pipelines, list)
        assert skillsets[0].pipelines[0].name == "legacy-pipeline"
