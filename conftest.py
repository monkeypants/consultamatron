"""Root conftest — ensure all BC source containers are importable.

Runtime BC discovery (practice.bc_discovery) adds source containers to
sys.path dynamically. This conftest does the same at test collection
time so that BC-internal test modules (e.g. personal/knowledge-iteration/
tests/) can import their own packages.
"""

from pathlib import Path

from practice.bc_discovery import source_container_dirs, ensure_on_sys_path

_REPO_ROOT = Path(__file__).resolve().parent

for _dir in source_container_dirs(_REPO_ROOT):
    ensure_on_sys_path(_dir)
