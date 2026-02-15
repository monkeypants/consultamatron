"""Generic entity store protocol.

Replaces six entity-specific repository protocols with a single
generic interface. Designed for #44; part of the #29 target
architecture.

All identity and scoping is expressed through string-keyed filters.
Entities carry their own identity and scope fields, so save(entity)
is self-contained.

Filter values are always strings. Enum fields compare naturally
because all domain enums extend str (str, Enum).

Mapping from current repository protocols
==========================================

SkillsetRepository -> EntityStore[Skillset]
-------------------------------------------
  get(name)                -> get({"name": name})
  list_all()               -> search()

ProjectRepository -> EntityStore[Project]
-----------------------------------------
  get(client, slug)        -> get({"client": client, "slug": slug})
  list_all(client)         -> search({"client": client})
  list_filtered(client,    -> search({"client": client,
    skillset, status)            "skillset": skillset,
                                 "status": status.value})
  save(project)            -> save(project)
  delete(client, slug)     -> delete({"client": client, "slug": slug})
  client_exists(client)    -> usecase logic: search({"client": client}) != []

DecisionRepository -> EntityStore[DecisionEntry]
------------------------------------------------
  get(client, project_slug, id) -> get({"client": client,
                                        "project_slug": project_slug,
                                        "id": id})
  list_all(client, project_slug) -> search({"client": client,
                                            "project_slug": project_slug})
  list_filtered(client,          -> search({"client": client,
    project_slug, title)                    "project_slug": project_slug,
                                            "title": title})
  save(entry)                    -> save(entry)

EngagementRepository -> EntityStore[EngagementEntry]
----------------------------------------------------
  get(client, id)          -> get({"client": client, "id": id})
  list_all(client)         -> search({"client": client})
  save(entry)              -> save(entry)

ResearchTopicRepository -> EntityStore[ResearchTopic]
-----------------------------------------------------
  get(client, filename)    -> get({"client": client, "filename": filename})
  list_all(client)         -> search({"client": client})
  save(topic)              -> save(topic)
  exists(client, filename) -> usecase logic: get({...}) is not None

TourManifestRepository -> EntityStore[TourManifest]
---------------------------------------------------
  get(client, project_slug,  -> get({"client": client,
    tour_name)                       "project_slug": project_slug,
                                     "name": tour_name})
  list_all(client,           -> search({"client": client,
    project_slug)                      "project_slug": project_slug})
  save(manifest)             -> save(manifest)

Specialized methods removed
===========================
  client_exists  -> usecase queries engagement store
  exists         -> usecase calls get() and checks for None
"""

from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel, covariant=True)


@runtime_checkable
class EntityStore(Protocol[T]):
    """Generic store for domain entities.

    Single protocol replacing all entity-specific repositories.
    Scoping and identity are expressed through string-keyed filters.
    Immutability is a usecase concern, not a store concern.
    """

    def get(self, filters: dict[str, str]) -> T | None:
        """Retrieve a single entity matching all filters.

        Returns None if no match.
        """
        ...

    def search(self, filters: dict[str, str] | None = None) -> list[T]:
        """List entities matching all filters.

        None or empty filters returns all entities in the store's
        scope. Each filter is a field-name to string-value pair.
        """
        ...

    def save(self, entity: T) -> None:
        """Save an entity (create or update).

        The entity carries its own identity and scope. Save semantics
        (upsert vs append) are an implementation detail.
        """
        ...

    def delete(self, filters: dict[str, str]) -> bool:
        """Delete entity matching filters. Returns True if deleted."""
        ...
