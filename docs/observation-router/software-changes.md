---
type: specification
---

# Software Change Specification

What needs to change in the platform to support needs-driven
observation routing. This is a specification sketch — it identifies
the changes needed but does not prescribe implementation detail.

## New: observation needs protocol

Every observation destination follows a convention — declare
information needs so the observation process can serve them.

- **Type-level needs:** Define generic observation needs for each
  destination type (client workspace, skillset, engagement, project,
  practice layer). These live with the type definitions.
- **Instance-level needs:** Each specific destination can extend
  type-level needs with its own. These live with the destination
  (client knowledge pack, skillset config, engagement brief, etc.).
- **Format:** Not yet specified. The protocol is the convention;
  the format will emerge from implementation.

## New: observation needs aggregation (CLI use case)

A CLI command that aggregates relevant needs into a brief:

    practice observation-needs --client X --engagement Y

The use case:
1. Identifies which destinations are relevant (client, active
   skillsets, engagement, projects, practice layer)
2. Gathers type-level needs for each destination type
3. Gathers instance-level needs for each specific destination
4. Synthesises into a brief the observing skill can consume

The skill at the inflection point calls this command and receives
the aggregated brief. It does not need to know about destinations,
types, or inheritance.

## Skill changes at inflection points

Each inflection point skill gains a step at the beginning:

1. Request the observation needs brief from the CLI
2. Hold the brief alongside the rich transient context
3. After the skill's primary work, apply the brief to extract
   observations that serve declared needs
4. Output observations for routing

### Review skill

The review is the comprehensive sweep — the brief is at its fullest.
Review applies the full brief to the full engagement context.
Observations made here serve any needs that opportunistic observation
missed.

### Gatepoint handling

Lightweight. The brief is available but the agent applies it only to
what surfaced during the gate negotiation. Must not slow down or
complicate gate negotiation — observation is a side channel.

### Negotiate loop

Multi-scope. The brief covers all destinations. The agent applies it
both to the substantive content of the negotiation and to pedagogic
signals from operator engagement. Pedagogic gradient descent is one
reflection strategy applied here, serving operator evidence tree
needs.

### Pack-and-wrap

Local only. Does not request the cross-context needs brief. The pack
itself declares what it needs observed during compilation (structural
integrity, cross-reference validity, summarisation strategy fitness).

## Routing infrastructure

A routing use case that:

- Accepts observations from any inflection point
- Dispatches to the destinations whose needs the observation serves
- Handles fan-out — a single observation may serve needs from
  multiple destinations
- Is extensible — new destination types participate by declaring
  needs, not by modifying routing logic

Routing is nearly mechanical because observations made in response
to declared needs already carry their destination. The routing
mechanism maps needs to destinations and delivers.

## What does NOT change

- Client workspace structure (already a knowledge pack)
- Pack convention (already supports the accumulation pattern)
- Engagement lifecycle (observation is additive, not restructuring)
- Integration surface capabilities (client workspace participates
  in existing capabilities)
- Propose-negotiate-agree loop (observation is a step within existing
  skills, not a new skill)
