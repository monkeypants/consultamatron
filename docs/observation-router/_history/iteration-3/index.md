---
name: iteration-3-software-changes-spec
purpose: >
  Compressed output of iteration 3. Updated the stale software-changes
  specification to reflect all design decisions from iterations 1-2,
  grounded in the existing platform architecture.
---

# Iteration 3 — Software Changes Specification

Updated the software-changes spec from a vague sketch ("format not
yet specified") to a concrete specification grounded in existing
platform patterns.

## Conversation arc

1. Operator chose updating the software-changes spec over
   implementation or platform article writing.
2. Agent read existing codebase patterns: `src/practice/entities.py`
   (Pydantic entity conventions), `src/practice/usecase.py` (UseCase
   protocol), `src/practice/repositories.py` (repository protocol
   conventions), `bin/cli/usecases.py` and `bin/cli/dtos.py` (CLI
   use case and DTO patterns).
3. Rewrote `software-changes.md` entirely. The old spec had five
   sections; the new spec has ten, structured around the existing
   architecture.
4. Recompiled bytecodes for the item and parent pack.
5. Operator chose to stack immediately — single-objective iteration
   complete.

## What changed in the spec

**Added: design constraints section.** Three constraints that govern
all implementation decisions — storage format (markdown+frontmatter,
Pydantic entities, semantic waist), guiding principle (actionability),
security posture (deny-all).

**Added: concrete entities.** `ObservationNeed` (slug, owner_type,
owner_ref, level, need, rationale, lifecycle_moment, served flag),
`RoutingAllowList` with `RoutingDestination` (derived from engagement
config), `Observation` (slug, source_inflection, need_refs, content,
destinations). Three destination classes integrated into the allow
list entity.

**Added: repository protocols.** `NeedsReader` (type_level_needs,
instance_needs) and `ObservationWriter`. Follows the existing
`@runtime_checkable Protocol` pattern from `repositories.py`.

**Added: three use cases.** `AggregateNeedsBrief` (the CLI command
with 5-step flow including duplicate flagging), `RouteObservations`
(mechanical dispatch with allow list verification), `ReviewNeedsHygiene`
(four failure modes). Replaces the single "routing infrastructure"
section.

**Added: needs lifecycle support.** Distributed declaration moments
per destination type, authoring by lifecycle phase.

**Added: needs evolution support.** Within-engagement self-feeding
(gatepoint N→N+1 via side-effect need writing), cross-engagement
promotion (instance→type at review).

**Expanded: skill changes.** Added evolution side effects — skills
write new needs. Review gains promotion role. Gatepoint gains
self-feeding evolution.

**Added to unchanged list.** Engagement configuration surface — no
new fields needed, routing policy derives from existing config.

**Removed.** "Pedagogic gradient descent" reference from negotiate
loop (too specific for a platform spec).

## Agreed summarisation strategies (for this compression)

- Preserve: what changed in the spec (the point of the iteration),
  codebase patterns consulted
- Compress: reading/research phase to key conclusions
- Drop: file read mechanics, bytecode compilation rounds, lint/test
  verification
- Organisation: single document under `_history/iteration-3/`
