"""Scaffold infrastructure for creating and updating skillset stub packages.

Creates bounded context packages with __init__.py files that export
SKILLSETS declarations and registers them in pyproject.toml.
"""

from __future__ import annotations

import re
from pathlib import Path


class SkillsetScaffold:
    """Creates and updates skillset stub packages.

    A stub package is a Python package with __init__.py that exports
    a SKILLSETS list. The scaffold also manages the pyproject.toml
    packages list to ensure new packages are discoverable.
    """

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root
        self._src_root = repo_root / "src"

    def _package_dir(self, name: str) -> Path:
        """Return the filesystem path for a skillset package."""
        return self._src_root / name.replace("-", "_")

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
        self._add_to_pyproject(name)
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

    def _add_to_pyproject(self, name: str) -> None:
        """Add the package to pyproject.toml's packages list."""
        pyproject_path = self._repo_root / "pyproject.toml"
        content = pyproject_path.read_text()

        # The relative path from repo root into src/
        pkg_path = f"src/{name.replace('-', '_')}"

        # Match the packages = [...] line and append if not present
        pattern = r"(packages\s*=\s*\[)([^\]]*?)(\])"
        match = re.search(pattern, content)
        if match is None:
            return

        existing = match.group(2)
        if pkg_path in existing:
            return

        # Add the new package before the closing bracket
        if existing.rstrip().endswith('"'):
            new_packages = existing.rstrip() + f', "{pkg_path}"'
        else:
            new_packages = existing + f'"{pkg_path}"'

        content = (
            content[: match.start()]
            + match.group(1)
            + new_packages
            + match.group(3)
            + content[match.end() :]
        )
        pyproject_path.write_text(content)


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
    parts = [
        f'"""{display_name} bounded context."""\n',
        "",
        "from practice.entities import Skillset",
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
