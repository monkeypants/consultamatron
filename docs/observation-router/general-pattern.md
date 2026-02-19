---
type: concept
---

# The General Pattern

Observations are captured at natural inflection points and routed to
knowledge contexts that declared a need for them. The pattern has
four stages:

**Inflection point → Needs brief → Observations → Routing**

An inflection point is a moment where the agent has rich context that
is about to be lost — a gatepoint negotiation, an engagement review,
a pack-and-wrap compilation, a negotiate loop. The observation needs
brief tells the agent what to look for in that transient context.

## Stages

1. **Inflection point.** A natural boundary in the engagement flow
   where the agent holds temporary context. The agent recognises it
   has arrived at such a point.

2. **Needs brief.** The agent requests an observation needs brief
   from the CLI. The CLI aggregates declared information needs from
   relevant destinations — the client workspace, the active
   skillsets, the engagement, the practice layer — and synthesises
   them into a brief. The agent now knows what the destinations are
   looking for.

3. **Observations.** The agent applies the needs brief to the rich
   context it currently holds. High-freedom activity — judgment about
   what in the current context serves declared needs, what is new,
   what contradicts prior understanding. The needs brief focuses
   attention; the agent's judgment extracts value.

4. **Routing.** Observations are dispatched to the destinations whose
   needs they serve. Routing is nearly mechanical because observations
   made in response to declared needs already carry their origin —
   the need identifies the destination.

## Key architectural insights

**Needs-driven observation.** Destinations are expert on their own
information needs. The observation process gathers requirements from
destinations before analysing the context. "What's relevant?" is
answered by "what do the consumers need?"

**Observation/routing split.** Observation (applying the brief to
rich context) is high-freedom judgment work. Routing (dispatching to
declared destinations) is low-freedom mechanical work. Separating
them means the observation mechanism can be rich and varied while
the routing mechanism stays simple and reliable.

**Classification collapses.** In the earlier formulation, observations
were made first and classified afterward. With needs-driven
observation, classification is nearly free — observations made in
response to a specific destination's need already know where they
are going. The classify-then-route step collapses because the need
carried its origin.

## Every inflection point is a moment of transient context

The agent holds context that is about to be lost. The needs brief's
job is to direct the agent's attention so it can extract durable
value from that transient context before it evaporates.
