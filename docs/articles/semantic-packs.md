# Semantic Packs

A general-purpose knowledge artifact type for managing bodies of
knowledge at dual fidelity. Observed first in org-research output,
the pattern recurs wherever Consultamatron maintains a corpus of
content that agents consume and humans audit.

## 1. The pattern

A semantic pack is a convention applied to a directory of markdown
files. Three things make a directory a knowledge pack:

1. An `index.md` at the root with manifest frontmatter (purpose,
   actor-goals, triggers)
2. Markdown files with minimal frontmatter (`type:`) and prose bodies
3. A `_bytecode/` directory mirroring the item tree with generated
   summaries

Optionally, a `summary.md` provides a human-authored prose synthesis
of the pack's contents.

```
{root}/
├── index.md         ← manifest only: purpose, actor-goals, triggers
├── summary.md       ← human-friendly prose synthesis (authored, not generated)
├── _bytecode/       ← compiled mirror: summary prose for each item (generated)
└── .../*.md         ← items: type frontmatter + prose body (human-maintained)
```

Every semantic pack provides two access paths to the same knowledge:

- **Human path**: `summary.md` → item bodies (prose, citations,
  narrative — readable but token-expensive)
- **Agent path**: `_bytecode/` mirror (compressed summaries, same
  tree structure — navigable without reading full items)

Neither path is subordinate. The human path exists for transparency
and the propose-negotiate-agree loop. The agent path exists for
downstream skill consumption where token budgets matter.

## 2. Separation of content and compiled metadata

Items are pure content. Summaries are compiled artifacts. They live
in separate places.

**Items** have minimal frontmatter (just `type:`) and a prose body.
The body is human-authored, iterated, and maintained. Items are never
modified by the pack-and-wrap use case.

```markdown
---
type: article
---
# The Semantic Waist

Full prose about the semantic waist concept, design rationale,
how it enables skill composition, testing strategy...
```

**`_bytecode/` files** are generated summary prose. No frontmatter.
Each file mirrors an item's path and contains a compressed
representation of that item's body.

```
_bytecode/semantic-waist.md:

The semantic waist routes engagement bookkeeping through a narrow
typed layer. Entities, repositories, use cases, DTOs. Captures
lifecycle data, not content. Enables skill composition through a
single source of truth for engagement state.
```

An agent reads `_bytecode/semantic-waist.md` (tiny, just summary),
decides it's relevant, then reads `semantic-waist.md` (full prose).
Progressive disclosure through the filesystem.

The `_` prefix signals "generated, don't edit" — same convention as
`__pycache__`. Design-time `_bytecode/` directories can be version
controlled or gitignored depending on context.

### Where structured data lives

- **Type** lives on items (minimal frontmatter, one line)
- **Summary** lives in `_bytecode/` (generated prose)
- **Manifest** lives on `index.md` (purpose, actor-goals, triggers)

Use cases read type from item frontmatter and summary from
`_bytecode/`, assembling a complete view when structured operations
are needed. Agents browsing `_bytecode/` don't need type info — they
navigate summaries to decide what to drill into. Type matters to
domain-specific use cases (jedi council selecting luminaries, research
checking citations) that know where to look.

## 3. Progressive disclosure through nesting

Items can be leaves (files) or composites (directories with their
own `index.md`). This is recursive — a composite item is itself a
knowledge pack:

```
items/
├── kent-beck.md                    ← leaf item
├── craig-larman/                   ← composite item (nested pack)
│   ├── index.md                    ← manifest for this sub-pack
│   ├── summary.md
│   ├── _bytecode/
│   ├── grasp/                      ← nested again
│   │   ├── index.md
│   │   ├── _bytecode/
│   │   ├── information-expert.md
│   │   ├── creator.md
│   │   └── low-coupling.md
│   ├── less.md
│   └── larman-laws.md
└── alistair-cockburn.md            ← leaf item
```

Each level has the same structure. The parent's `_bytecode/` contains
a summary of the child pack (compiled from the child's manifest and
items). The parent never descends into the child's items — it trusts
the child's compilation.

Knowledge trees grow where attention goes. You start with a leaf
(`craig-larman.md`), it grows, you promote it to a composite
(`craig-larman/`), and one branch (`grasp/`) grows its own children.
The tree is lopsided because knowledge is lopsided. Reorganisation
is cheap — moving an item means moving a file and recompiling the
immediate parent.

## 4. The pack-and-wrap operation

Pack-and-wrap reads item bodies and generates `_bytecode/` entries.
Items are never modified.

1. Walk items in one pack (one level, not recursive)
2. For each leaf item: read body, generate summary, write to
   `_bytecode/` mirror path
3. For each composite item: read the child's `_bytecode/` to generate
   the parent-level summary

Pack-and-wrap operates one level at a time. If a nested pack's items
changed, compile it first, then the parent. Bottom-up propagation,
each step is small.

The summary generation step requires LLM cost per changed item. The
compilation step (writing to `_bytecode/`) is mechanical. Detecting
staleness: if an item's modification time is newer than its
`_bytecode/` mirror, it needs recompilation.

### Incremental adoption

Any existing directory of markdown files can become a knowledge pack
incrementally:

1. Add `index.md` with manifest frontmatter → directory is a pack
2. Add `type:` frontmatter to existing files → items are typed
3. Run pack-and-wrap → `_bytecode/` generated with summaries

Each step adds value independently. Step 1 alone is enough for an
agent to decide "should I look in here?"

## 5. The manifest

The `index.md` frontmatter is the pack's self-description. It carries
the metadata needed to decide whether to consume the pack without
reading any content.

Two concerns, separated:

- **Actor-goals**: who benefits and what they get (value proposition).
  Each entry declares an actor and their goal. This is the Information
  Expert pattern (Larman) — the pack that has the knowledge also has
  the self-description.

- **Triggers**: situations that make the pack relevant (activation
  condition). Separate from actor-goals because the same trigger
  activates multiple actor-goals, and the same actor-goal may be
  activated by different triggers. Agents match on triggers; humans
  match on actor-goals.

```yaml
---
name: platform-architecture
purpose: >
  Architectural knowledge for extending and maintaining Consultamatron.
actor_goals:
  - actor: skill author
    goal: understand conformance requirements for a new BC
  - actor: contributor
    goal: learn CLI command generation and docstring conventions
  - actor: human/AI dyad
    goal: understand design rationale during development sessions
triggers:
  - adding a new bounded context
  - adding a CLI command
  - debugging conformance test failures
  - executing skillset engineering skills
---
```

The manifest is a specification (Fowler) that consumers match against.
"Am I the right actor? Is this the right trigger? Does this pack serve
my goal?"

The index.md body contains routing instructions: "humans read
`summary.md`, agents read `_bytecode/`."

## 6. The PackItem protocol

Items declare their type in frontmatter. The protocol is minimal:

```python
class PackItem(Protocol):
    """Any item in a knowledge pack."""
    name: str
    item_type: str
```

Name is derived from the filename. Type is the frontmatter `type:`
field. Use cases read item frontmatter for type when they need
structured operations (selecting luminaries, filtering by type).
Agents browsing `_bytecode/` don't interact with the protocol — they
just read summaries.

Concrete item types add their own semantics but items remain simple
markdown files. A pantheon's items have `type: luminary`. A docs
pack's items have `type: article`. A pack can declare a default type
in its manifest for packs where all items share a type.

## 7. Two lifecycle contexts

Semantic packs appear in two distinct contexts with different
ownership and lifecycle characteristics.

### Runtime packs (engagement execution)

Live in client workspaces. Created by agents during engagement work.
Owned by the engagement.

```
clients/{org-slug}/resources/
├── index.md              ← manifest (gate artifact for org-research)
├── summary.md            ← human-friendly synthesis
├── _bytecode/            ← compiled summaries
└── reports/
    ├── corporate-overview.md
    ├── market-position.md
    └── technology-stack.md
```

Each report is a typed item. The org-research skill produces these.
Downstream skills read `_bytecode/` summaries to decide which reports
to read in full.

### Design-time packs (skillset engineering)

Live in source containers. Created by skill authors during skillset
development. Owned by the bounded context.

```
commons/{bc}/skills/{skill}/references/{pack-name}/
├── index.md              ← manifest
├── summary.md
├── _bytecode/
└── methods/
    ├── standard-research.md
    ├── market-landscape.md
    └── operator-mediated.md
```

Each method file has type frontmatter. The research use case reads
`_bytecode/` summaries to present available strategies.

### The distinction matters

| | Runtime packs | Design-time packs |
|---|---|---|
| **Lives in** | `clients/` (gitignored) | `commons/`, `personal/`, `partnerships/` |
| **Created by** | Engagement execution use cases | Skillset engineering use cases |
| **Contains** | Client-specific findings | Domain-generic methodologies |
| **Lifecycle** | Engagement-scoped, potentially refreshed | Version-controlled, evolves with skillset |
| **Example** | Organisation research output | Research strategy catalogue |

Pack-and-wrap does not distinguish between these contexts. It operates
on the convention, not on content semantics or storage location.

## 8. Knowledge packs as pluggable adapters

A skill may declare one or more knowledge packs that it requires. The
use case that executes the skill loads those packs and makes them
available during execution. This is dependency injection for knowledge.

### Multiple packs per skill

A skill is not limited to a single knowledge pack. Different aspects
of a skill's execution may draw on different bodies of knowledge:

```
{skill}/references/
├── research-strategies/     ← plugged into research use cases
│   ├── index.md
│   ├── summary.md
│   ├── _bytecode/
│   └── methods/
├── messaging-patterns/      ← plugged into engagement polishing use cases
│   ├── index.md
│   ├── summary.md
│   ├── _bytecode/
│   └── patterns/
└── analytical-frameworks/   ← plugged into analysis use cases
    ├── index.md
    ├── summary.md
    ├── _bytecode/
    └── frameworks/
```

Each pack serves a different adapter. The packs share the same
convention; the adapters that consume them are different.

### Strategy selection

One common adapter pattern is strategy selection: given a knowledge
pack of methodologies, select the appropriate one (or synthesise a
hybrid) for the current context.

The agent reads `_bytecode/` summaries to understand available
strategies, selects or combines based on engagement context, and
the operator approves the selection. New strategies are added to
the pack (open to extension) without modifying the use case or
SKILL.md (closed to modification).

### The adapter is not the pack

The semantic pack is a content convention — it knows how to describe
and compress knowledge. The adapter is the use case behaviour that
consumes the pack for a specific purpose. Strategy selection is one
adapter. Others might include:

- **Reference lookup**: find the relevant framework for a problem domain
- **Template selection**: select a communication pattern for a deliverable
- **Jedi council**: select luminaries whose perspectives to invoke
  for multi-perspective analysis

The pack provides uniform access to knowledge. The adapter provides
domain-specific interpretation.

## 9. The Open/Closed Principle applied

The semantic pack pattern embodies OCP at two levels.

### Pack content is open to extension

Adding a new research strategy, analytical framework, or luminary
means adding a markdown file with `type:` frontmatter and re-running
pack-and-wrap to generate its `_bytecode/` summary. No code changes.
No SKILL.md modifications.

### Pack consumption is open to extension

New adapters can consume existing packs without modifying the pack
or the pack-and-wrap use case. A research strategy pack authored for
`wm-research` can be consumed by a hypothetical `scenario-planning`
skill — it reads the same `_bytecode/` through a different adapter.

The core defines the pack convention (closed). Skills define how they
consume packs (open).

## 10. Relationship to the research protocol

Issue #34 proposes structured research entities (Source,
LiteratureNote, Topic, Report) to make citation density a
deterministic business rule. The semantic pack convention provides
the content infrastructure those entities inhabit.

- `Source` maps to a typed item (`type: source`)
- `LiteratureNote` maps to the evidence relationship in item content
- `Topic` maps to a composite item grouping related sources
- `Report` maps to a leaf item with full prose

The research domain model (#34) defines what research IS — the
entities and their invariants. The semantic pack defines how research
is STORED and DESCRIBED — the content convention. The research
protocol defines how research is CONSUMED — the adapter contracts
between packs and skills.

These three concerns compose without coupling:

1. **Domain model** (entities, invariants) — `practice.entities`
2. **Content convention** (items, `_bytecode/`, manifest) — semantic packs
3. **Consumption contracts** (adapter protocols) — research protocol

## 11. Structural enforcement

### Doctrine test: pack shape

A conformance test can verify that every semantic pack has the
required structure: `index.md` exists with valid manifest frontmatter,
items have `type:` frontmatter. Same pattern as pipeline coherence
and gate consumes tests.

### Doctrine test: compilation freshness

A conformance test can verify that `_bytecode/` is not stale: if any
item is newer than its `_bytecode/` mirror, the pack needs
recompilation. This catches the case where a skill author adds
content but forgets to re-run pack-and-wrap.

These tests apply uniformly to both runtime and design-time packs.
The test fixture discovers packs by the presence of `index.md` with
manifest frontmatter, not by hard-coded paths.

## 12. Current state and next steps

The pattern exists implicitly in org-research output. It has not been
extracted as a named concept with structural enforcement.

**What exists today:**
- org-research produces research with reports, summary, and index —
  but compression is encoded in SKILL.md prose, not in a protocol
  or use case
- org-research has a single `research-strategies.md` reference file —
  not yet a design-time pack
- `docs/` is a half-formed design-time pack: articles and conventions
  about the platform, consumed by skill authors, contributors, and
  human/AI dyads

**What this article proposes (Option B: note the pattern, build
incrementally):**
1. Name the pattern (done — this article)
2. Define the KnowledgePack entity model and PackItem protocol (#98)
3. Implement pack-and-wrap use cases, test on `docs/` (#99)
4. Build the research domain model (#34), using pack infrastructure
5. Extract design-time packs when skillsets need them

Any directory of markdown files becomes a knowledge pack the moment
it gets an `index.md` with manifest frontmatter and its files get
`type:` frontmatter. Pack-and-wrap compiles `_bytecode/` summaries.
Agents navigate `_bytecode/` for cheap progressive disclosure, read
full items only when needed.
