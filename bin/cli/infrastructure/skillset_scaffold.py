"""Scaffold infrastructure for creating and updating skillset stub packages.

Creates bounded context packages with __init__.py files that export
SKILLSETS declarations.  New packages are placed under ``commons/``.
"""

from __future__ import annotations

from pathlib import Path


class SkillsetScaffold:
    """Creates and updates skillset stub packages.

    A stub package is a Python package with __init__.py that exports
    a SKILLSETS list.  New packages are placed under ``commons/``.
    """

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    def _package_dir(self, name: str) -> Path:
        """Return the filesystem path for a skillset package."""
        return self._repo_root / "commons" / name.replace("-", "_")

    def create(
        self,
        name: str,
        display_name: str,
        description: str,
        slug_pattern: str,
        problem_domain: str = "",
        value_proposition: str = "",
        deliverables: list[str] | None = None,
        classification: list[str] | None = None,
        evidence: list[str] | None = None,
    ) -> Path:
        """Create a stub BC package with a SKILLSETS declaration.

        Also generates a stub presenter, PRESENTER_FACTORY export, and
        test directory so the package passes all conformance tests from
        the moment it is created.

        Returns the path to the created __init__.py.
        """
        pkg_dir = self._package_dir(name)
        pkg_dir.mkdir(parents=True, exist_ok=True)
        init_py = pkg_dir / "__init__.py"
        init_py.write_text(
            _render_init(
                name=name,
                display_name=display_name,
                description=description,
                slug_pattern=slug_pattern,
                problem_domain=problem_domain,
                value_proposition=value_proposition,
                deliverables=deliverables or [],
                classification=classification or [],
                evidence=evidence or [],
            )
        )

        # Stub presenter
        presenter_py = pkg_dir / "presenter.py"
        if not presenter_py.exists():
            presenter_py.write_text(_render_presenter(name, display_name))

        # Test directory
        tests_dir = pkg_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        tests_init = tests_dir / "__init__.py"
        if not tests_init.exists():
            tests_init.write_text("")
        test_presenter = tests_dir / "test_presenter.py"
        if not test_presenter.exists():
            pkg_python = name.replace("-", "_")
            test_presenter.write_text(_render_test_presenter(name, pkg_python))

        return init_py

    def update(
        self,
        name: str,
        display_name: str | None = None,
        description: str | None = None,
        slug_pattern: str | None = None,
        problem_domain: str | None = None,
        value_proposition: str | None = None,
        deliverables: list[str] | None = None,
        classification: list[str] | None = None,
        evidence: list[str] | None = None,
    ) -> Path:
        """Update an existing stub package's SKILLSETS declaration.

        Reads the current __init__.py, applies changes, rewrites it.
        Returns the path to the updated __init__.py.
        """
        pkg_dir = self._package_dir(name)
        init_py = pkg_dir / "__init__.py"

        current = _parse_current_skillset(init_py, name)

        init_py.write_text(
            _render_init(
                name=name,
                display_name=display_name
                if display_name is not None
                else current.display_name,
                description=description
                if description is not None
                else current.description,
                slug_pattern=slug_pattern
                if slug_pattern is not None
                else current.slug_pattern,
                problem_domain=problem_domain
                if problem_domain is not None
                else current.problem_domain,
                value_proposition=value_proposition
                if value_proposition is not None
                else current.value_proposition,
                deliverables=deliverables
                if deliverables is not None
                else current.deliverables,
                classification=classification
                if classification is not None
                else current.classification,
                evidence=evidence if evidence is not None else current.evidence,
            )
        )
        return init_py


def _render_init(
    name: str,
    display_name: str,
    description: str,
    slug_pattern: str,
    problem_domain: str,
    value_proposition: str,
    deliverables: list[str],
    classification: list[str],
    evidence: list[str],
) -> str:
    """Render the __init__.py content for a skillset stub package."""
    pkg_python = name.replace("-", "_")
    parts = [
        f'"""{display_name} bounded context."""\n',
        "",
        "from practice.entities import Skillset",
        "",
        "",
        "def _create_presenter(workspace_root, repo_root):",
        f"    from {pkg_python}.presenter import {_class_name(name)}Presenter",
        "",
        f"    return {_class_name(name)}Presenter(workspace_root=workspace_root)",
        "",
        "",
        f"PRESENTER_FACTORY = ({name!r}, _create_presenter)",
        "",
        "SKILLSETS: list[Skillset] = [",
        "    Skillset(",
        f"        name={name!r},",
        f"        display_name={display_name!r},",
        f"        description={description!r},",
        f"        slug_pattern={slug_pattern!r},",
    ]
    if problem_domain:
        parts.append(f"        problem_domain={problem_domain!r},")
    if value_proposition:
        parts.append(f"        value_proposition={value_proposition!r},")
    if deliverables:
        parts.append(f"        deliverables={deliverables!r},")
    if classification:
        parts.append(f"        classification={classification!r},")
    if evidence:
        parts.append(f"        evidence={evidence!r},")
    parts.extend(
        [
            "    ),",
            "]",
            "",
        ]
    )
    return "\n".join(parts)


def _class_name(kebab_name: str) -> str:
    """Convert a kebab-case name to PascalCase."""
    return "".join(word.capitalize() for word in kebab_name.split("-"))


def _render_presenter(name: str, display_name: str) -> str:
    """Render a stub presenter module."""
    cls = _class_name(name)
    return f'''"""{display_name} project presenter."""

from __future__ import annotations

from pathlib import Path

from practice.content import ProjectContribution
from practice.entities import Project


class {cls}Presenter:
    """Assembles {display_name} workspace artifacts into structured content."""

    def __init__(self, workspace_root: Path) -> None:
        self._ws_root = workspace_root

    def present(self, project: Project) -> ProjectContribution:
        return ProjectContribution(
            slug=project.slug,
            title=project.slug,
            skillset=project.skillset,
            status=project.status.value,
            hero_figure=None,
            overview_md="",
            sections=[],
        )
'''


def _render_test_presenter(name: str, pkg_python: str) -> str:
    """Render a stub presenter test module."""
    cls = _class_name(name)
    return f'''"""Tests for {cls}Presenter."""

from __future__ import annotations

from datetime import date

import pytest

from practice.content import ProjectContribution
from practice.entities import Project, ProjectStatus
from {pkg_python}.presenter import {cls}Presenter


@pytest.mark.doctrine
class TestPresenterContract:
    """{cls}Presenter produces valid ProjectContribution."""

    def test_produces_project_contribution(self, tmp_path):
        presenter = {cls}Presenter(workspace_root=tmp_path)
        project = Project(
            slug="test-1",
            client="test-corp",
            engagement="strat-1",
            skillset={name!r},
            status=ProjectStatus.ELABORATION,
            created=date(2025, 6, 1),
        )
        result = presenter.present(project)
        assert isinstance(result, ProjectContribution)
        assert result.slug == "test-1"
        assert result.skillset == {name!r}
        assert isinstance(result.sections, list)
'''


def _parse_current_skillset(init_py: Path, name: str):
    """Parse the current Skillset from an __init__.py file.

    Uses exec to evaluate the module in a controlled namespace.
    """
    from practice.entities import Skillset

    namespace: dict = {"Skillset": Skillset}
    exec(compile(init_py.read_text(), str(init_py), "exec"), namespace)
    skillsets = namespace.get("SKILLSETS", [])
    for s in skillsets:
        if s.name == name:
            return s
    msg = f"Skillset {name!r} not found in {init_py}"
    raise ValueError(msg)
