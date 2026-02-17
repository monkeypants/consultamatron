"""Shared BC package discovery for all three source containers.

Single source of truth for finding bounded context packages at runtime.
Scans ``commons/``, ``personal/``, and ``partnerships/{slug}/`` for
directories containing ``__init__.py`` with a ``SKILLSETS`` attribute.

The ``pyproject.toml`` packages list is *not* consulted here — it exists
only for hatch build/editable-install.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

from practice.entities import Skillset


def source_container_dirs(repo_root: Path) -> list[Path]:
    """Return existing source container directories.

    Returns ``commons/``, ``personal/`` (if present), and each
    ``partnerships/{slug}/`` subdirectory (if present).
    """
    dirs: list[Path] = []

    commons = repo_root / "commons"
    if commons.is_dir():
        dirs.append(commons)

    personal = repo_root / "personal"
    if personal.is_dir():
        dirs.append(personal)

    partnerships = repo_root / "partnerships"
    if partnerships.is_dir():
        for child in sorted(partnerships.iterdir()):
            if child.is_dir():
                dirs.append(child)

    return dirs


def ensure_on_sys_path(directory: Path) -> None:
    """Add *directory* to ``sys.path`` if not already present."""
    path_str = str(directory)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


def scan_bc_packages(source_dir: Path) -> list[ModuleType]:
    """Import BC packages from *source_dir* and return those with SKILLSETS.

    Adds *source_dir* to ``sys.path`` persistently, then imports each
    subdirectory containing ``__init__.py`` that exports ``SKILLSETS``.
    """
    if not source_dir.is_dir():
        return []

    ensure_on_sys_path(source_dir)

    modules: list[ModuleType] = []
    for child in sorted(source_dir.iterdir()):
        if not child.is_dir() or not (child / "__init__.py").is_file():
            continue
        try:
            mod = importlib.import_module(child.name)
            if hasattr(mod, "SKILLSETS"):
                modules.append(mod)
        except ImportError:
            continue
    return modules


def discover_all_bc_modules(repo_root: Path) -> list[ModuleType]:
    """Scan all source containers and return every BC module."""
    modules: list[ModuleType] = []
    for container_dir in source_container_dirs(repo_root):
        modules.extend(scan_bc_packages(container_dir))
    return modules


def collect_skillsets(source_dir: Path) -> list[Skillset]:
    """Scan *source_dir* for BC packages and return their skillsets."""
    result: list[Skillset] = []
    for mod in scan_bc_packages(source_dir):
        result.extend(getattr(mod, "SKILLSETS", []))
    return result
