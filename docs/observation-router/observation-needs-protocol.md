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
  "watch for signals about the CTO's appetite for build-vs-buy"
- A particular skillset extends with needs driven by known gaps —
  "watch for cases where the evolution assessment stage takes too long"
- A particular engagement extends with needs driven by its brief —
  "watch for evidence that the stated problem is a symptom of
  something deeper"

Instance-level needs are the pecadilloes — specific to the target,
declared by whoever knows the target best (the operator, the
engagement brief, accumulated client knowledge).

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

## Needs grow through practice

Type-level needs evolve as the practice matures — new generic needs
are added when a pattern is observed across multiple engagements.
Instance-level needs evolve as specific targets develop — the client
workspace accumulates knowledge that refines what it needs to learn
next.

This replaces the earlier "bag of tricks" concept. The bags were
vague — "questions worth asking, grow with experience." Declared
needs are concrete, owned by their destinations, and aggregated
mechanically.

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
