"""Minimal frontmatter parser for knowledge pack and skill manifests.

Extracts ``key: value`` pairs from ``---``-delimited YAML-like
frontmatter without an external YAML dependency.  Handles flat
scalars and the ``>`` folded-scalar continuation used for
multi-line descriptions.
"""

from __future__ import annotations

from pathlib import Path


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Extract frontmatter key-value pairs from a markdown file.

    Returns an empty dict when the file has no ``---`` delimiters
    or only a single delimiter (incomplete frontmatter).
    """
    text = path.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}

    result: dict[str, str] = {}
    current_key: str | None = None
    folding = False
    fold_lines: list[str] = []

    for line in parts[1].splitlines():
        stripped = line.strip()
        if not stripped:
            if folding:
                fold_lines.append("")
            continue

        # Indented continuation of a folded scalar
        if folding and line[0] in (" ", "\t"):
            fold_lines.append(stripped)
            continue

        # Flush any accumulated folded text
        if folding:
            result[current_key] = " ".join(ln for ln in fold_lines if ln)
            folding = False
            fold_lines = []

        if ":" not in stripped:
            continue

        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()

        if value == ">":
            current_key = key
            folding = True
            fold_lines = []
        elif value:
            result[key] = value
        else:
            result[key] = ""

    # Flush trailing folded scalar
    if folding:
        result[current_key] = " ".join(ln for ln in fold_lines if ln)

    return result


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
