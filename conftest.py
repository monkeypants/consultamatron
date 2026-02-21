"""Root conftest — ensure all BC package directories are importable.

Runtime BC discovery (practice.bc_discovery) adds BC package directories
to sys.path dynamically. This conftest does the same at test collection
time so that BC-internal test modules (e.g. commons/*/skillsets/*/tests/)
can import their own packages.
"""

from pathlib import Path

from practice.bc_discovery import bc_package_dirs, ensure_on_sys_path

_REPO_ROOT = Path(__file__).resolve().parent

for _dir in bc_package_dirs(_REPO_ROOT):
    ensure_on_sys_path(_dir)
