---
type: concept
---

# Observation Needs Protocol

Observation destinations declare their information needs. The
observation process gathers these needs before analysing context.
This is the protocol that makes needs-driven observation work.

## The protocol: know your own information needs

Every observation destination — a client workspace, a skillset, an
engagement, a project, the practice layer — follows a convention:
declare what kinds of observations you need. The destination is expert
on its own needs.

This is analogous to actor-goals in pack manifests. The pack declares
who consumes it and what they need from it. Observation destinations
declare what they need to learn from engagement activity — they are
actors with goals for sensory input.

## Guiding principle: what are we able to improve?

Information needs are driven by the ability to act on the information.
The purpose of observations is to drive behaviour: continuous
improvement, demonstrating responsiveness to the client, operant
conditioning to reinforce positive habits, solving problems,
mitigating risks, achieving goals.

A need is worth declaring when the destination can act on the
observation — change a process, refine a methodology step, adjust
delivery to a client preference. Needs that produce observations
nobody can act on are noise. The test for a well-formed need: "if
the observer finds something, what improves?"

## Inheritance model

Individual observation targets inherit generic needs from their type
and may extend with their own specifics.

**Type-level needs (generic):**
- All client workspaces need observations about stakeholder dynamics,
  constraints, preferences, decision-making patterns
- All skillsets need observations about what worked, what didn't,
  missing steps, better framings
- All engagements need observations about process effectiveness and
  workflow friction
- The practice layer needs observations about infrastructure gaps
  and tooling needs

**Instance-level needs (specific):**
- A particular client extends with needs driven by their situation —
  "watch for signals about the sponsor's appetite for build-vs-buy"
- A particular skillset extends with needs driven by known gaps —
  "watch for cases where the evolution assessment stage takes too long"
- A particular engagement extends with needs driven by its brief —
  "watch for evidence that the stated problem is a symptom of
  something deeper"

Instance-level needs are the pecadilloes — specific to the target,
declared by whoever knows the target best (the operator, the
engagement brief, accumulated client knowledge).

## Needs lifecycle

Needs declaration is not a single event — it is distributed across
the destination's lifecycle. Each destination type has multiple
moments where needs are naturally created, refined, or retired.
These moments already exist in the practice; the observation-routing
system piggybacks on them.

### Client workspace needs

- **Research** — initial needs emerge from what we learn about the
  client ("regulated industry — watch for compliance constraints")
- **Engagement planning** — needs refined by engagement scope ("this
  engagement focuses on go-to-market — watch for channel assumptions")
- **During engagement** — gatepoint observations reveal gaps in
  client knowledge (feedback loop)
- **Engagement review** — retrospective: "what should we watch for
  next time we work with this client?"
- **Between engagements** — needs age. Some become more urgent, some
  become irrelevant as the client evolves.

### Engagement needs

- **Planning** — "what risks should we watch for in this engagement?"
- **During execution** — gatepoint feedback loop refines what to
  watch for
- **Review** — less about refining engagement needs (it's ending) and
  more about promoting patterns to type-level

### Skillset needs

- **ns-design** — what signals does each pipeline stage need to know
  if it's working?
- **ns-implement** — are the declared needs actually observable?
- **rs-assess** — what is the skillset blind to? What signals is it
  not collecting?
- **rs-iterate** — what signals confirm the improvement worked?
- **During execution** — do declared needs actually produce useful
  observations?

### Personal needs

- **Goal setting** — intentional: "I want to get better at X"
- **During engagement** — emergent: operator notices their own
  confusion or mastery
- **Personal review** — reflective: "what did I learn, what gaps
  remain?"

### Practice layer needs

- **Practice planning** — "what infrastructure improvements do we
  need?"
- **During engagement** — friction and tooling gaps surface
  operationally
- **Post-review pattern recognition** — "this keeps coming up across
  engagements"

### Who authors needs

Distributed across the lifecycle like the declaration moments.
At research and planning, the operator. At gatepoints, the agent
proposes based on observations. At review, both reflect. At
skillset engineering, the skillset author. The authoring follows
the lifecycle — whoever is active at that moment is the natural
author.

## Needs evolution

Needs evolve at two timescales.

**Within an engagement.** Observations at gatepoint N produce needs
for gatepoint N+1. The observation system feeds itself — the act of
observing something interesting is also the act of declaring a need
for the next inflection point.

**Across engagements.** Patterns noticed in one engagement become
instance-level needs. The same pattern noticed across several
engagements gets promoted to type-level. The review skill is the
natural moment for promotion — "this thing we kept watching for
should be something we always watch for."

Type-level needs evolve through this promotion path: instance →
pattern → type. Each promotion is a methodology improvement
observation routed to the type-level needs definition.

This replaces the earlier "bag of tricks" concept. The bags were
vague — "questions worth asking, grow with experience." Declared
needs are concrete, owned by their destinations, and evolve through
well-defined lifecycle moments.

## Needs hygiene

Needs have a full lifecycle: creation, refinement, and retirement.
Without active maintenance, needs accumulate and degrade.

**Staleness.** The context has changed and this need no longer
applies — "watch for the CTO's build-vs-buy appetite" when the CTO
has left. Needs degrade like any knowledge artifact.

**Duplication.** Instance-level needs may overlap with type-level
needs that were added later, or multiple instance needs from
different gatepoints may converge on the same thing.

**Supersession.** A vague early need was replaced by a more specific
one but the vague one was never removed.

**Unserved needs.** A need exists but no observation has ever
addressed it. Two possible causes: the need is wrong (prune it) or
the observation process has a blind spot (investigate it). The
distinction matters.

**Review moments** for needs hygiene align with the declaration
lifecycle:
- Engagement planning — review client needs from previous
  engagements. Still relevant?
- Engagement review — which needs were served? Which produced
  nothing?
- rs-assess — review skillset needs. Duplicative? Stale?
- Personal review — achieved goals can be retired.

The aggregation use case can flag duplicates mechanically when
building the brief — if two needs are textually similar or serve
the same destination, surface that for the operator.

## The aggregation use case

A CLI use case aggregates relevant needs into an observation needs
brief:

1. Identify which destinations are relevant at this inflection point
   (which client, which skillsets, which engagement, which projects)
2. Gather type-level needs for each destination type
3. Gather instance-level needs for each specific destination
4. Synthesise into a brief the observing skill can consume

The skill at the inflection point does not need to know about
destinations, types, or inheritance. It asks the CLI for the
observation needs brief and receives a synthesised document.

## Where needs are declared

Needs declarations live with their owners:
- Client workspace needs: in the client knowledge pack
- Skillset needs: in the skillset's metadata or configuration
- Engagement needs: in the engagement brief or configuration
- Project needs: in the project's decision log or configuration
- Practice needs: in the practice layer documentation
- Type-level needs: in the type definitions (what it means to be
  a client workspace, a skillset, etc.)

## Storage format

Needs declarations follow the practice convention: markdown files
with structured data in YAML frontmatter and prose body as docstring.
A repository implementation serialises/deserialises the frontmatter
into Pydantic entities (per `src/practice/entities.py`), so use
cases operate in Python land through the semantic waist rather than
in LLM land. The prose body provides context for agent consumption
when the brief is rendered for an inflection point.

This matches the existing pattern: entities define the domain model,
repositories handle persistence, use cases orchestrate behaviour —
all through the narrow typed layer between practice and skillsets.
