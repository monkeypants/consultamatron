---
type: concept
---

# The Observation/Routing Architectural Split

The separation of observation from routing is the key architectural
decision in this pattern. Needs-driven observation sharpens the split
further — the needs brief mediates between routing destinations and
the observation process.

## Two activities, different freedom

**Observation** is high-freedom. The agent applies the needs brief to
rich transient context, using judgment to extract what serves declared
needs. The brief focuses attention; the agent decides what it finds.

**Routing** is low-freedom. Observations made in response to declared
needs already carry their destination. Dispatch is mechanical — the
need identifies where the observation goes.

## Why the split matters

Combining observation and routing into one step creates a coupling
problem. An observation mechanism that also handles routing must know
about all possible destinations, their formats, and their intake
protocols.

The needs brief decouples them further. The observation skill does
not know about destinations at all — it receives a synthesised brief
and applies it to context. The routing mechanism does not know about
context — it receives classified observations and dispatches them.
The CLI's aggregation use case is the only component that knows about
both sides.

## Classification collapses into needs

In the earlier formulation, observations were made first, then
classified by domain, then routed. With needs-driven observation,
classification is nearly free — an observation made in response to
a client workspace's declared need is already classified as "client."
The classify-then-route pipeline simplifies to route.

Some observations may serve multiple needs from multiple destinations.
The routing mechanism handles fan-out — a single observation can
route to multiple destinations whose needs it serves.

## Pipeline and opportunistic coexist

The engagement review is a deliberate, comprehensive reflection point
— all relevant needs are in scope. But observations can also be made
at any gatepoint or negotiate loop — the needs brief is available at
any inflection point.

These are not competing approaches. Review serves needs that
opportunistic observation missed. Opportunistic observation serves
needs while context-rich signal is still loaded. Both consume the
same needs brief mechanism; they differ in when and how thoroughly
they apply it.

## Council consensus (preserved)

The jedi council consensus reinforced the observation/routing split:
- **Larman:** Review classifies, routing dispatches — separate
  concerns. Structure must make routing the path of least resistance.
- **Parnas:** Three kinds of knowledge change independently — they
  should be in different modules. The interface between them is what
  was missing.
- **Cunningham:** CRC cards for routing responsibilities — Client
  Knowledge Steward, Methodology Improvement Router, Practice
  Improvement Router.

The needs-driven approach fulfils these positions — the "interface
between modules" (Parnas) is the observation needs protocol. The
"path of least resistance" (Larman) is the CLI-aggregated brief that
the skill simply asks for.
