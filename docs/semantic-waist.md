# The Semantic Waist

Why Consultamatron routes bookkeeping through a narrow structured data
layer, and what that buys us.

## The problem: context diffusion

A consulting engagement produces a lot of text. Research sub-reports,
needs documents, supply chain decompositions, evolution assessments,
strategic plays, atlas analyses, tour prose. Each artifact captures
understanding that subsequent work depends on.

Without structure, that understanding is encoded in natural language,
distributed across files, in formats that vary between skills. When a
downstream skill needs to know "what stage is this project at?" or "what
decisions have been made?", it has two options:

1. **Re-read everything.** Parse the prose, infer the state. This costs
   thousands of tokens, is slow, and is unreliable. Different models
   parse the same prose differently. The same model parses it
   differently on different days.

2. **Guess.** Assume the state based on which files exist. This is
   cheaper but even less reliable. A file existing does not mean its
   content is correct or complete.

Both approaches burn expensive inference to recover information that was
known precisely at the moment it was produced. The information was there;
it just wasn't captured in a form that machines can consume cheaply.

This is context diffusion: valuable convergent conclusions dissolving
into prose where they become expensive to recover.

## The design double diamond

Consulting work follows the design double diamond repeatedly. Each cycle
has a divergent phase (explore, research, generate options) and a
convergent phase (synthesise, narrow, agree). The convergent phase
produces a commitment: "these are the user needs," "this is the supply
chain," "this is the strategy."

```
  Diverge        Converge        Diverge        Converge
     /\              /\              /\              /\
    /  \            /  \            /  \            /  \
   /    \    ===   /    \    ===   /    \    ===   /    \
  /      \  WAIST /      \  WAIST /      \  WAIST /      \
 /        \/     /        \/     /        \/     /        \

 research   needs    chain    evolve   strategy   deliverable
```

The `===` marks are the semantic waist: narrow points where diffuse
understanding crystallises into structured data. Each waist captures the
value of the preceding convergence and makes it available — cheaply,
reliably, deterministically — to the next divergence.

The gate artifacts at each waist point are the deterministic backbone of
the pipeline. The `.agreed` suffix marks the boundary between
nondeterministic LLM proposals (divergent exploration, synthesis,
drafting) and deterministic committed state (the operator has confirmed
this artifact). Gate artifacts are immutable after agreement — to change
one, re-negotiate and iterate, do not overwrite. This immutability is
what makes the waist trustworthy: downstream consumers know that an
`.agreed` file will not change under them.

## What the waist is made of

The structured data layer (`bin/cli/`) implements the waist as clean
architecture:

```
entities.py      Domain objects: Project, DecisionEntry, EngagementEntry,
                 ResearchTopic, Skillset, PipelineStage

repositories.py  Protocols: how entities are stored and retrieved
                 (no implementation details, just contracts)

usecases.py      Business rules: what operations are valid, what
                 invariants must hold

dtos.py          Request/response pairs: typed contracts between the
                 CLI shell and usecases

main.py          CLI shell: argument parsing, output formatting
                 (no business logic)
```

Skills interact with this layer through wrapper scripts (shell scripts
in each skill's `scripts/` directory, per the Agent Skills standard).
The wrapper script encodes skill-specific knowledge — which fields a
stage-3 decision needs, which status transition to make — and calls the
CLI. The CLI validates, persists, and reports.

### What makes it a waist

It is narrow: 7 write usecases, 6 read usecases. Every bookkeeping
operation in every skill passes through one of these 13 operations.

It is typed: Pydantic entities enforce field presence, types, and value
constraints. A `ProjectStatus` can only be one of four values. A
`DecisionEntry` always has an id, client, project_slug, date, title,
and fields dict.

It is validated: usecases enforce business rules. You cannot skip a
status transition. You cannot register a project with an unknown
skillset. You cannot record a decision for a project that does not
exist.

It is cheap: a CLI call costs microseconds and zero tokens. The same
operation done by an LLM writing markdown costs thousands of tokens and
is less reliable.

## Why this matters: value lock-in

Each time a skill records a decision through the CLI, it locks in the
value of the preceding divergent work. The insight does not evaporate
when the context window ends. It does not degrade when a different model
reads it later. It is captured as structured data that any consumer —
site renderer, progress checker, another skill, a future skill that does
not exist yet — can use reliably.

This is the progress capture mechanism. The waist converts expensive
inference into cheap structured data. Subsequent divergent work starts
from the concentrated residue of previous convergence rather than
re-deriving it from prose.

### The cost asymmetry

Bookkeeping operations — "record this decision," "update project
status," "register this research topic" — are the lowest-value
activities for an LLM and the highest-risk for accuracy. An LLM
formatting a markdown decision entry might get the date format wrong,
forget a field, or write it to the wrong file. The CLI cannot get these
wrong — validation is in the usecase, format is in the repository.

This frees the LLM to do what it is actually good at: divergent
research, convergent synthesis, analytical judgment. The CLI does
bookkeeping; the model does thinking.

### Information density for downstream consumers

When the `engage` skill assesses client state, it calls
`project progress` — one CLI call that returns the current pipeline
stage, completed stages, and next prerequisite. This is the concentrated
output of potentially weeks of engagement work, available in
milliseconds.

When the site renderer builds the deliverable site, it reads projects
and research topics through repository queries, then delegates to
per-skillset presenters that assemble workspace artifacts into generic
content entities. It does not parse markdown artifacts to determine
project structure.

When the `review` skill inventories what happened during an engagement,
it reads the decision log and engagement log — complete audit trails in
structured form.

Each of these consumers gets high information density from the waist
without re-mining the source artifacts.

### External artifacts as cross-session memory

Decision logs, gate files, and engagement logs are not just
documentation. They are the agent's context reconstruction mechanism.
Each new session rebuilds understanding from these artifacts rather than
relying on conversation history. The agent reads the engagement log to
learn what happened, the decision log to learn what was decided, and the
gate files to learn what was agreed. This reconstruction is cheap because
the waist provides it as structured data, not prose to be re-mined.

This is what makes multi-session engagements viable. Without the waist,
each session would start from raw artifacts and spend thousands of tokens
recovering state. With the waist, each session starts from the
concentrated residue of all previous sessions — the same information at
a fraction of the cost.

## The boundary: lifecycle vs content

The current domain model captures **lifecycle** data: that projects
exist, that decisions were made, that stages completed, that research
was registered. It is generic to consulting — it knows nothing about
Wardley Map components, BMC building blocks, or supply chain structure.

This genericity is valuable. New skillsets get bookkeeping for free.
The lifecycle layer does not change when a new consulting methodology
is added.

There is a natural question about whether the waist should also capture
**content** data: the components in a map, the segments in a canvas,
the dependencies in a supply chain. This would enable per-component
browsing, cross-artifact validation, and richer downstream assembly.

The lifecycle layer captures *that* things happened. A content layer
would capture *what* was produced.

This is a future architectural decision. The lifecycle layer has clear
immediate value and should be completed first. When the content layer
is needed, the same clean architecture patterns (entities, repositories,
usecases, typed DTOs) apply. The waist gets wider but retains its
structural properties: typed, validated, cheap.

## DDD vocabulary for the waist

The semantic waist and the bounded context architecture already
implement several DDD strategic patterns. Naming them makes the
architecture more navigable for contributors familiar with DDD
vocabulary.

### Shared Kernel

The `resources/` directory is a shared kernel — research output that all
skillsets consume but no individual skillset owns. `resources/index.md`
is the kernel's primary artifact. Changes to its schema affect every
consumer: `wm-research` reads it, `bmc-research` reads it, `engage`
reads it. Minimise this surface. When adding fields to
`resources/index.md`, treat it as a cross-team schema change.

### Published Language

The `resources/index.md` format, `brief.agreed.md` structure, and gate
artifact schemas are the published language between the engagement layer
and skillsets. Each skillset knows how to read the published language.
Each skill that produces a gate artifact writes in the published
language. Documenting these schemas as explicit contracts (field names,
required sections, optional extensions) makes the published language
testable.

### Anti-Corruption Layer

Each skillset's research skill translates the neutral published language
into domain-specific terms. `wm-research` turns research into "anchors,"
"components," and "evolution stages." `bmc-research` turns research into
"customer segments" and "value propositions." This translation is the
anti-corruption layer — it prevents domain concepts from leaking across
bounded context boundaries. The neutral research stays neutral; the
domain-specific interpretation stays local.

### Context Map

The `engage` skill functions as an executable context map. It discovers
available bounded contexts, proposes which to use for a given client,
and describes cross-project relationships ("a Wardley Map could inform
BMC Key Resources"). The engagement plan it produces is literally a map
of which contexts participate and how they relate.

## Implications for skill design

### Skills should not do bookkeeping inline

Before the waist, skills contained formatting instructions:

> Append to `decisions.md`:
> ```markdown
> ## {Date} — Stage 2: User needs agreed
> **Agreed**: ...
> ```

After the waist, skills call a wrapper script:

```bash
scripts/record-agreement.sh --client "$CLIENT" --project "$PROJECT" \
  --title "Stage 2: User needs agreed" \
  --field "Users=$USERS" --field "Scope=$SCOPE"
```

The wrapper calls `consultamatron decision record`. The CLI validates,
formats, and persists. The skill never touches the storage format.

### Skills should read from the waist, not from files

A skill that needs to know project state should call
`consultamatron project progress`, not scan for `.agreed.md` files.
A skill that needs the decision history should call
`consultamatron decision list`, not parse `decisions.md`.

This means skills work correctly even if the storage format changes.
It means they get validated, structured data instead of raw text. And
it means the operation costs zero tokens.

### The waist enables skill composition

Because the waist is the single source of truth for engagement state,
skills that have never heard of each other can compose. A future
business plan skill can read the project registry and decision logs to
understand what analytical work has been done — without knowing anything
about Wardley Mapping or BMC internals. Skillset-specific content
(WM atlas views and narrative presentations, BMC canvas blocks) stays
behind per-skillset presenter boundaries.

The waist is the API between skills. Each skill writes its convergent
conclusions into it. Each skill reads its preconditions from it.

## Relationship to OWM

OWM (Online Wardley Maps DSL) is the existence proof that inspired this
approach. OWM is a narrow semantic waist for map content: a small,
well-defined format that multiple tools (renderer, editor, online
viewer) consume reliably. Issue #12 explicitly cites OWM as the
precedent.

The CLI's structured data layer applies the same principle to engagement
lifecycle data. OWM captures map content; the CLI captures the
consulting process around it.

## Testing the waist

The waist is tested at three layers:

- **Entities** (`test_entities.py`): domain objects construct correctly,
  enums behave, status transitions follow rules
- **Usecases** (`test_usecases.py`): business rules hold — duplicates
  rejected, not-found errors raised, progress computed correctly from
  decision logs matched against pipeline definitions
- **CLI** (`test_cli.py`): argument parsing, output formatting, error
  surfacing — the thin shell around usecases

These are fast, deterministic, and cheap. They run in under a second
with no network, no LLM, no file I/O (in-memory repositories). This is
the waist testing itself: structured data in, structured data out,
business rules enforced.

## Summary

The semantic waist is a deliberate architectural choice: route all
bookkeeping through a narrow, typed, validated, deterministic software
layer. This captures the value of expensive convergent work as cheap
structured data, preserves context across sessions and models, and
provides a high-density foundation for subsequent divergent work.

It is not a convenience. It is the mechanism by which Consultamatron
accumulates institutional knowledge across engagements without burning
tokens to reconstruct what it already knows.
