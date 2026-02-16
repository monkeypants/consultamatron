"""Skillset repository that aggregates SKILLSETS from BC modules.

Discovers bounded context packages dynamically by reading the packages
list from pyproject.toml, importing each, and collecting those that
export a SKILLSETS attribute.
"""

from __future__ import annotations

import importlib
import tomllib
from pathlib import Path

from practice.entities import Skillset


def _read_pyproject_packages(pyproject_path: Path) -> list[str]:
    """Read the packages list from pyproject.toml.

    Looks in [tool.hatch.build.targets.wheel].packages and converts
    filesystem paths (e.g. "src/practice") to importable module names
    (e.g. "practice").
    """
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    packages = (
        data.get("tool", {})
        .get("hatch", {})
        .get("build", {})
        .get("targets", {})
        .get("wheel", {})
        .get("packages", [])
    )

    names = []
    for pkg in packages:
        # "src/practice" -> "practice", "wardley_mapping" -> "wardley_mapping"
        name = Path(pkg).name
        names.append(name)
    return names


class CodeSkillsetRepository:
    """Aggregates SKILLSETS attributes from bounded context modules.

    Discovers packages from pyproject.toml, imports each, and collects
    those with a SKILLSETS: list[Skillset] attribute.
    """

    def __init__(self, repo_root: Path) -> None:
        self._skillsets: list[Skillset] = []
        packages = _read_pyproject_packages(repo_root / "pyproject.toml")
        for pkg_name in packages:
            try:
                mod = importlib.import_module(pkg_name)
                self._skillsets.extend(getattr(mod, "SKILLSETS", []))
            except ImportError:
                continue

    def get(self, name: str) -> Skillset | None:
        for s in self._skillsets:
            if s.name == name:
                return s
        return None

    def list_all(self) -> list[Skillset]:
        return list(self._skillsets)
