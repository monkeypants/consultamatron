"""Frontmatter parser for knowledge pack and skill manifests.

Extracts YAML frontmatter from ``---``-delimited markdown files using
``yaml.safe_load``.  Returns a ``dict[str, Any]`` preserving nested
structures (lists, dicts) that the flat parser previously lost.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def parse_frontmatter(path: Path) -> dict[str, Any]:
    """Extract frontmatter key-value pairs from a markdown file.

    Returns an empty dict when the file has no ``---`` delimiters,
    only a single delimiter (incomplete frontmatter), or malformed YAML.
    """
    text = path.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}

    try:
        parsed = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return {}

    if not isinstance(parsed, dict):
        return {}

    return parsed
