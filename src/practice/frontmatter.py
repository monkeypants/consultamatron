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


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse ``---``-delimited frontmatter from a string.

    Returns ``(metadata, body)`` where *metadata* is a flat dict of
    key-value pairs and *body* is everything after the closing ``---``.
    Returns ``({}, text)`` when no valid frontmatter is found.
    """
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    result: dict[str, str] = {}
    for line in parts[1].splitlines():
        stripped = line.strip()
        if not stripped or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        result[key.strip()] = value.strip()

    return result, parts[2].lstrip("\n")


def format_frontmatter(metadata: dict[str, str], body: str) -> str:
    """Produce a ``---``-delimited frontmatter block followed by *body*."""
    lines = ["---"]
    for key, value in metadata.items():
        lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n" + body
