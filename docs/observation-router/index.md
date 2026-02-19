---
name: observation-router
purpose: >
  Design specification for the observation-and-routing pattern. How the
  practice captures useful observations at natural inflection points and
  routes them to knowledge contexts that declared a need for them. Working
  toward a platform article and software changes.
actor_goals:
  - actor: platform engineer
    goal: understand what software changes are needed to support observation routing
  - actor: skill author
    goal: know which inflection points produce observations and how the needs brief drives them
  - actor: operator
    goal: understand how learnings from engagements are captured and where they go
triggers:
  - designing the observation routing infrastructure
  - adding observation support to existing skills
  - declaring observation needs for a destination
  - reviewing engagement output for routing
  - extending the review skill with needs-driven observation
---

# Observation Router

Design specification for capturing and routing observations at natural
inflection points in the consulting practice.

## Status

Iteration 2 in progress. Worked example traces the pattern through
a fictional engagement. Needs protocol refined with guiding principle
and storage format decision.

## Routing

Agents: read accumulator items for current understanding. For
background on how we got here, read `_history/` bytecodes (most
recent first). Humans: start with `general-pattern.md`, then browse
items by interest.

## Accumulator items (persist, evolve across iterations)

| Item | Type | What it covers |
|---|---|---|
| `general-pattern.md` | concept | The four-stage pattern: inflection point → needs brief → observations → routing |
| `inflection-point-taxonomy.md` | concept | Four inflection point types with context character and needs brief scope |
| `observation-needs-protocol.md` | concept | Destinations declare information needs; inheritance model; CLI aggregation use case |
| `observation-routing-split.md` | concept | High-freedom observation vs low-freedom routing; classification collapses into needs |
| `routing-security-model.md` | concept | Deny-all/allow-some routing policy; three destination classes (personal, engagement-scoped, commons/dark channel); information leak as primary risk |
| `software-changes.md` | specification | Platform changes: needs protocol, CLI use case, skill changes, routing infrastructure |
| `worked-example.md` | scenario | End-to-end trace through a fictional engagement gatepoint |

## History

- `_history/iteration-1/` — extraction of accumulator items from
  iteration-0, needs-driven model refinement, Beck-Larman testing
  deliberation, eligibility council + operator security correction.
- `_history/iteration-0/` — compressed output of the conversation that
  identified the general pattern, ran a jedi council deliberation on
  client expertise accumulation, and refined the observation-routing
  architecture through operator negotiation.
