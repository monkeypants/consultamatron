"""Content hashing for bytecode freshness detection.

SHA-256 hashes replace mtime comparisons for determining whether
a bytecode mirror is up-to-date with its source item.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def hash_content(text: str) -> str:
    """Return ``sha256:<hex>`` digest of *text*."""
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


def hash_children(bytecode_dir: Path) -> str:
    """Hash the concatenated contents of child bytecode files.

    Files are sorted by name to ensure deterministic output.
    Returns ``sha256:<hex>`` digest of the concatenation.
    """
    parts: list[str] = []
    for child in sorted(bytecode_dir.iterdir()):
        if child.is_file() and child.suffix == ".md":
            parts.append(child.read_text())
    return hash_content("".join(parts))
