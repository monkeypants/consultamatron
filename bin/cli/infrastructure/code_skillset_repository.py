"""Skillset repository that aggregates SKILLSETS from BC modules.

Discovers bounded context packages from three source containers:

1. **commons** — packages listed in pyproject.toml (committed)
2. **personal** — BC packages in ``{repo_root}/personal/`` (gitignored)
3. **partnerships** — BC packages in ``{repo_root}/partnerships/{slug}/``
   (gitignored, one subdirectory per partnership)

All three containers use the same discovery mechanism: scan for
subdirectories containing ``__init__.py``, import them, and collect
those that export a ``SKILLSETS`` attribute.
"""

from __future__ import annotations

import importlib
import sys
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


def _scan_directory(source_dir: Path) -> list[Skillset]:
    """Import BC packages from an arbitrary directory and collect SKILLSETS.

    Iterates subdirectories containing ``__init__.py``, temporarily
    adds *source_dir* to ``sys.path``, imports the module, and
    collects any ``SKILLSETS`` attribute.
    """
    if not source_dir.is_dir():
        return []

    result: list[Skillset] = []
    path_str = str(source_dir)
    added = path_str not in sys.path

    if added:
        sys.path.insert(0, path_str)
    try:
        for child in sorted(source_dir.iterdir()):
            if not child.is_dir() or not (child / "__init__.py").is_file():
                continue
            try:
                mod = importlib.import_module(child.name)
                result.extend(getattr(mod, "SKILLSETS", []))
            except ImportError:
                continue
    finally:
        if added and path_str in sys.path:
            sys.path.remove(path_str)

    return result


class CodeSkillsetRepository:
    """Aggregates SKILLSETS from all three source containers.

    Commons packages are discovered via pyproject.toml (already on
    sys.path thanks to hatch).  Personal and partnership packages are
    discovered by scanning their directories for BC packages.
    """

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root
        self._skillsets: list[Skillset] = []

        # Commons — packages listed in pyproject.toml
        packages = _read_pyproject_packages(repo_root / "pyproject.toml")
        for pkg_name in packages:
            try:
                mod = importlib.import_module(pkg_name)
                self._skillsets.extend(getattr(mod, "SKILLSETS", []))
            except ImportError:
                continue

        # Personal and partnerships
        self._skillsets.extend(self._scan_source_dirs())

    def get(self, name: str) -> Skillset | None:
        for s in self._skillsets:
            if s.name == name:
                return s
        return None

    def list_all(self) -> list[Skillset]:
        return list(self._skillsets)

    def _scan_source_dirs(self) -> list[Skillset]:
        """Scan personal/ and partnerships/{slug}/ for BC packages."""
        result: list[Skillset] = []

        # Personal
        result.extend(_scan_directory(self._repo_root / "personal"))

        # Partnerships — each subdirectory is a separate partnership
        partnerships_dir = self._repo_root / "partnerships"
        if partnerships_dir.is_dir():
            for subdir in sorted(partnerships_dir.iterdir()):
                if subdir.is_dir():
                    result.extend(_scan_directory(subdir))

        return result
