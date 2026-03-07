"""Shared BC package discovery for all source containers.

Single source of truth for finding bounded context packages at runtime.
Source containers use a consistent layout convention:

    {source}/
    ├── skillsets/    # BC packages (scanned for PIPELINES attribute)
    ├── skills/       # Generic skills with SKILL.md
    └── ...           # Other content (knowledge packs, etc.)

Commons sources live under ``commons/{org}/{repo}/`` and are consumed
as git submodules.  Personal and partnership sources live at
``personal/`` and ``partnerships/{slug}/`` respectively.

The ``pyproject.toml`` packages list is *not* consulted here — it exists
only for hatch build/editable-install.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

from practice.entities import Pipeline


def bc_package_dirs(repo_root: Path) -> list[Path]:
    """Return directories that contain BC packages.

    Each returned path is a directory whose immediate children may be
    BC packages (directories with ``__init__.py`` exporting ``SKILLSETS``).

    Sources:
    - ``commons/{org}/{repo}/skillsets/`` (two levels of nesting)
    - ``personal/skillsets/`` (if present)
    - ``partnerships/{slug}/skillsets/`` (if present)
    """
    dirs: list[Path] = []

    # Commons: commons/{org}/{repo}/skillsets/
    commons = repo_root / "commons"
    if commons.is_dir():
        for org in sorted(commons.iterdir()):
            if not org.is_dir() or org.name.startswith("."):
                continue
            for repo in sorted(org.iterdir()):
                if not repo.is_dir():
                    continue
                skillsets_dir = repo / "skillsets"
                if skillsets_dir.is_dir():
                    dirs.append(skillsets_dir)

    # Personal: personal/skillsets/
    personal_ss = repo_root / "personal" / "skillsets"
    if personal_ss.is_dir():
        dirs.append(personal_ss)

    # Partnerships: partnerships/{slug}/skillsets/
    partnerships = repo_root / "partnerships"
    if partnerships.is_dir():
        for child in sorted(partnerships.iterdir()):
            if not child.is_dir():
                continue
            ss = child / "skillsets"
            if ss.is_dir():
                dirs.append(ss)

    return dirs


def skill_search_dirs(repo_root: Path) -> list[Path]:
    """Return directories to scan for SKILL.md files.

    - ``{repo_root}/skills/`` (repo-root generic skills)
    - ``personal/`` (full recursive scan)
    - ``partnerships/{slug}/`` (full recursive scan)
    - ``commons/{org}/{repo}/skillsets/`` (only skillset-owned skills)
    """
    dirs: list[Path] = []

    # Repo-root generic skills
    root_skills = repo_root / "skills"
    if root_skills.is_dir():
        dirs.append(root_skills)

    # Personal — full scan (skills/ and skillsets/)
    personal = repo_root / "personal"
    if personal.is_dir():
        dirs.append(personal)

    # Partnerships — full scan per slug
    partnerships = repo_root / "partnerships"
    if partnerships.is_dir():
        for child in sorted(partnerships.iterdir()):
            if child.is_dir():
                dirs.append(child)

    # Commons — only skillset-owned skills (not top-level skills/)
    commons = repo_root / "commons"
    if commons.is_dir():
        for org in sorted(commons.iterdir()):
            if not org.is_dir() or org.name.startswith("."):
                continue
            for repo in sorted(org.iterdir()):
                if not repo.is_dir():
                    continue
                skillsets_dir = repo / "skillsets"
                if skillsets_dir.is_dir():
                    dirs.append(skillsets_dir)

    return dirs


def source_container_dirs(repo_root: Path) -> list[Path]:
    """Return existing source container directories.

    Legacy interface — returns ``commons/``, ``personal/`` (if present),
    and each ``partnerships/{slug}/`` subdirectory (if present).
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
    """Scan all BC package directories and return every BC module."""
    modules: list[ModuleType] = []
    for pkg_dir in bc_package_dirs(repo_root):
        modules.extend(scan_bc_packages(pkg_dir))
    return modules


def collect_pipelines(source_dir: Path) -> list[Pipeline]:
    """Scan *source_dir* for BC packages and return their pipelines."""
    result: list[Pipeline] = []
    for mod in scan_bc_packages(source_dir):
        result.extend(_get_pipelines(mod))
    return result


# Backwards-compatible alias
collect_skillsets = collect_pipelines
