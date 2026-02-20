"""Observation routing policy — the security boundary.

Pure functions that derive routing allow lists from engagement
configuration. Deny-all, allow-some. No I/O — takes already-resolved
data and returns structured results.
"""

from __future__ import annotations

from practice.entities import (
    Engagement,
    Project,
    RoutingAllowList,
    RoutingDestination,
    SkillsetSource,
    SourceType,
)


def build_routing_allow_list(
    *,
    client: str,
    engagement: Engagement,
    projects: list[Project],
    sources: list[SkillsetSource],
) -> RoutingAllowList:
    """Build the allow list for observation routing.

    Policy:
    - Personal, client, and practice are always allowed.
    - Engagement and project destinations are added when projects exist.
    - Partnership and personal source skillsets are allowed.
    - Commons skillsets are never allowed (flow through MCP).
    """
    seen: set[tuple[str, str]] = set()
    destinations: list[RoutingDestination] = []

    def _add(owner_type: str, owner_ref: str) -> None:
        key = (owner_type, owner_ref)
        if key not in seen:
            seen.add(key)
            destinations.append(
                RoutingDestination(owner_type=owner_type, owner_ref=owner_ref)
            )

    # Always allowed
    _add("personal", "personal")
    _add("client", client)
    _add("practice", "practice")

    # Projects imply engagement + per-project destinations
    if projects:
        _add("engagement", engagement.slug)
        for project in projects:
            _add("project", project.slug)

    # Source skillsets (skip commons)
    for source in sources:
        if source.source_type == SourceType.COMMONS:
            continue
        for skillset_name in source.skillset_names:
            _add("skillset", skillset_name)

    return RoutingAllowList(destinations=destinations)
