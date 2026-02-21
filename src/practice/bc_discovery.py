"""Shared BC package discovery for all three source containers.

Single source of truth for finding bounded context packages at runtime.
Scans ``commons/``, ``personal/``, and ``partnerships/{slug}/`` for
directories containing ``__init__.py`` with a ``PIPELINES`` attribute
(falling back to ``SKILLSETS`` for backward compatibility).

The ``pyproject.toml`` packages list is *not* consulted here — it exists
only for hatch build/editable-install.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

from practice.entities import Pipeline


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


def _has_pipelines(mod: ModuleType) -> bool:
    """True if *mod* exports PIPELINES or SKILLSETS."""
    return hasattr(mod, "PIPELINES") or hasattr(mod, "SKILLSETS")


def _get_pipelines(mod: ModuleType) -> list[Pipeline]:
    """Return pipelines from *mod*, preferring PIPELINES over SKILLSETS."""
    return getattr(mod, "PIPELINES", getattr(mod, "SKILLSETS", []))


def scan_bc_packages(source_dir: Path) -> list[ModuleType]:
    """Import BC packages from *source_dir* and return those with PIPELINES.

    Adds *source_dir* to ``sys.path`` persistently, then imports each
    subdirectory containing ``__init__.py`` that exports ``PIPELINES``
    (or the legacy ``SKILLSETS`` attribute).
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
            if _has_pipelines(mod):
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


def collect_pipelines(source_dir: Path) -> list[Pipeline]:
    """Scan *source_dir* for BC packages and return their pipelines."""
    result: list[Pipeline] = []
    for mod in scan_bc_packages(source_dir):
        result.extend(_get_pipelines(mod))
    return result


# Backwards-compatible alias
collect_skillsets = collect_pipelines
