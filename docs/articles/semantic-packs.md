# Semantic Packs

A general-purpose knowledge artifact type for managing bodies of
knowledge at dual fidelity. Observed first in org-research output,
the pattern recurs wherever Consultamatron maintains a corpus of
content that agents consume and humans audit.

## 1. The pattern

A semantic pack is a directory with an invariant shape:

```
{root}/
├── items/           ← long-form source material
├── summary.md       ← human-friendly prose synthesis, links to items
├── bytecode/        ← L1-L2 compressed semantic tree
└── index.md         ← L0 semantic bytecode index + pointer to summary.md
```

The content varies — research reports, methodology descriptions,
messaging frameworks, analytical lenses. The shape does not. Every
semantic pack provides two access paths to the same knowledge:

- **Human path**: `summary.md` → `items/*` (prose, citations,
  narrative — readable but token-expensive)
- **Agent path**: `index.md` → `bytecode/*` (compressed, routable,
  token-efficient — consumable but not meant for humans)

Neither path is subordinate. The human path exists for transparency
and the propose-negotiate-agree loop. The agent path exists for
downstream skill consumption where token budgets matter.

## 2. The pack-and-wrap operation

The transition from authored content to semantic pack is a
deterministic operation:

1. **Author** creates `items/*` (long-form, iterative, domain-specific)
2. **Author** creates or approves `summary.md` (synthesis, links to items)
3. **Pack-and-wrap** generates `bytecode/` and `index.md` from the
   approved items

Step 3 is mechanical. It takes approved human-readable content and
produces a token-efficient semantic bytecode hierarchy. It does not
require domain expertise, negotiation, or creative judgement. It is
a use case, not a skill.

The pack-and-wrap operation is the same regardless of what the pack
contains or where it lives. It reads items, compresses into an L1-L2
tree, and writes an L0 index. The content domain is irrelevant to the
compression.

### The semantic bytecode hierarchy

Three tiers, all token-efficient:

- **L2** (detail): one file per semantic cluster of related items.
  Summarises findings, uses precise vocabulary aligned with consumer
  needs, routes to specific items for evidence.
- **L1** (cluster): one file per group of related L2 files.
  Summarises and routes to L2 files, characterises what questions
  the cluster answers.
- **L0** (index): `index.md` at the pack root. Compressed summary of
  all content, routes to L1 clusters, points to `summary.md` for
  human access.

The L0 index is the standard entry point for agent consumption.
Downstream skills read `index.md` to navigate the pack. If they need
more detail, they follow routes to L1, then L2, then the original
items. This is progressive disclosure for token budgets — most
consumers never need to read the full items.

## 3. Two lifecycle contexts

Semantic packs appear in two distinct contexts with different
ownership and lifecycle characteristics.

### Runtime packs (engagement execution)

Live in client workspaces. Created by agents during engagement work.
Owned by the engagement.

```
clients/{org-slug}/resources/
├── reports/          ← items: research reports with citations
├── summary_prose.md  ← summary: synthesis of findings
├── bytecode/         ← L1-L2 compressed hierarchy
└── index.md          ← L0 index (gate artifact for org-research)
```

The org-research skill produces a runtime pack. The items are
research reports about a specific organisation. The pack-and-wrap
compresses them into semantic bytecode. Downstream skills
(`wm-research`, `bmc-research`, etc.) consume the index.

Runtime packs are engagement-scoped artefacts. They are created,
potentially refreshed, and consumed within the lifecycle of client
work. They live in `clients/`, which is gitignored.

### Design-time packs (skillset engineering)

Live in source containers. Created by skill authors during skillset
development. Owned by the bounded context.

```
commons/{bc}/skills/{skill}/references/{pack-name}/
├── methods/          ← items: methodology descriptions
├── summary.md        ← summary: overview of available methods
├── bytecode/         ← L1-L2 compressed hierarchy
└── index.md          ← L0 index
```

A skill author assembles reference materials — research strategies,
analytical frameworks, messaging patterns — and packs them for agent
consumption. The pack lives in the repository alongside the skill
that uses it.

Design-time packs are maintained through skillset engineering use
cases (the `ns-*` and `rs-*` skills). They evolve with the skillset,
not with any particular engagement.

### The distinction matters

| | Runtime packs | Design-time packs |
|---|---|---|
| **Lives in** | `clients/` (gitignored) | `commons/`, `personal/`, `partnerships/` |
| **Created by** | Engagement execution use cases | Skillset engineering use cases |
| **Contains** | Client-specific findings | Domain-generic methodologies |
| **Lifecycle** | Engagement-scoped, potentially refreshed | Version-controlled, evolves with skillset |
| **Example** | Organisation research output | Research strategy catalogue |

The pack-and-wrap use case does not distinguish between these contexts.
It operates on the directory structure, not on the content semantics
or storage location.

## 4. Knowledge packs as pluggable adapters

A skill may declare one or more knowledge packs that it requires. The
use case that executes the skill loads those packs and makes them
available during execution. This is dependency injection for knowledge.

### Multiple packs per skill

A skill is not limited to a single knowledge pack. Different aspects
of a skill's execution may draw on different bodies of knowledge:

```
{skill}/references/
├── research-strategies/     ← plugged into research use cases
│   ├── methods/
│   ├── summary.md
│   ├── bytecode/
│   └── index.md
├── messaging-patterns/      ← plugged into engagement polishing use cases
│   ├── methods/
│   ├── summary.md
│   ├── bytecode/
│   └── index.md
└── analytical-frameworks/   ← plugged into analysis use cases
    ├── methods/
    ├── summary.md
    ├── bytecode/
    └── index.md
```

Each pack serves a different adapter. Research strategy packs are
consumed by research use cases. Messaging pattern packs are consumed
by engagement polishing use cases. Analytical framework packs are
consumed by analysis use cases. The packs are the same shape; the
adapters that consume them are different.

### Strategy selection

One common adapter pattern is strategy selection: given a knowledge
pack of methodologies, select the appropriate one (or synthesise a
hybrid) for the current context.

The org-research skill currently does this with a single
`references/research-strategies.md` file. The SKILL.md says "read
the strategies, assess initial signals, propose which strategy to
use." With semantic packs, this becomes:

1. The research strategies are a design-time pack with individual
   method files in `methods/`
2. The research use case loads `research-strategies/index.md`
3. The agent reads the L0 index to understand available strategies
4. The agent selects or combines strategies based on engagement context
5. The operator approves the selection (propose-negotiate-agree)

New strategies are added to the pack (open to extension) without
modifying the research use case or the SKILL.md (closed to
modification). This is the Open/Closed Principle applied to domain
knowledge.

### The adapter is not the pack

The semantic pack is a content type — it knows how to store and
compress knowledge. The adapter is the use case behaviour that
consumes the pack for a specific purpose. Strategy selection is one
adapter. Others might include:

- **Reference lookup**: load a framework pack, find the relevant
  framework for a given problem domain
- **Template selection**: load a messaging pack, select the
  appropriate communication pattern for a deliverable type
- **Constraint checking**: load a compliance pack, verify that
  proposed output satisfies declared constraints

The pack provides uniform access to knowledge. The adapter provides
domain-specific interpretation. Separating these concerns means new
adapter types can be written without changing pack structure, and new
packs can be authored without changing adapter code.

## 5. The Open/Closed Principle applied

The semantic pack pattern embodies OCP at two levels.

### Pack content is open to extension

Adding a new research strategy, analytical framework, or messaging
pattern means adding a file to `items/` and re-running pack-and-wrap.
No code changes. No SKILL.md modifications. The pack's index
automatically reflects the new content.

Skillset authors extend the knowledge base by adding items. The
compression infrastructure is unchanged. Skill execution adapts
because it reads the index dynamically, not because it was modified
to handle the new item.

### Pack consumption is open to extension

New adapters can consume existing packs without modifying the pack
or the pack-and-wrap use case. A research strategy pack authored for
`wm-research` can be consumed by a hypothetical `scenario-planning`
skill that also needs research strategies — it reads the same index
through a different adapter.

This is the plugin architecture applied to knowledge: the core
defines the pack structure (closed), and skills define how they
consume packs (open).

## 6. Relationship to the research protocol

Issue #34 proposes structured research entities (Source,
LiteratureNote, Topic, Report) to make citation density a
deterministic business rule. The semantic pack pattern provides the
content infrastructure that those entities describe.

- `Source` maps to a citable item in `items/`
- `LiteratureNote` maps to the evidence relationship captured in
  the item's content
- `Topic` maps to the semantic cluster that groups related items
- `Report` maps to the L2 compression of a cluster

The research domain model (#34) defines what research IS — the
entities and their invariants. The semantic pack defines how research
is STORED and COMPRESSED — the content infrastructure. The research
protocol defines how research is CONSUMED — the adapter contracts
between packs and skills.

These three concerns compose without coupling:

1. **Domain model** (entities, invariants) — `practice.entities`
2. **Content infrastructure** (pack structure, compression) — semantic packs
3. **Consumption contracts** (adapter protocols) — research protocol

## 7. Structural enforcement

### Doctrine test: pack shape

A conformance test can verify that every semantic pack has the
required structure: `index.md` exists, `bytecode/` is populated when
items exist, `summary.md` references items. This is the same pattern
as pipeline coherence and gate consumes tests.

### Doctrine test: pack freshness

A conformance test can verify that pack compression is not stale:
if any item in `items/` is newer than `index.md`, the pack needs
re-compression. This catches the case where a skill author adds a
new methodology but forgets to re-run pack-and-wrap.

These tests apply uniformly to both runtime and design-time packs.
The test fixture discovers packs by directory shape, not by hard-coded
paths.

## 8. Current state and next steps

The pattern exists implicitly in org-research output. It has not been
extracted as a named concept with structural enforcement.

**What exists today:**
- org-research produces a runtime pack (reports, summary, bytecode,
  index) — but the shape is encoded in the SKILL.md prose, not in
  a protocol or use case
- org-research has a single `research-strategies.md` reference file —
  not yet a design-time pack
- The pack-and-wrap compression is performed by the org-research skill
  as part of its methodology — not yet extracted as a standalone use
  case

**What this article proposes (Option B: note the pattern, build
incrementally):**
1. Name the pattern (done — this article)
2. Build the research domain model and research use cases (#34),
   including pack-and-wrap as a use case
3. Extract the design-time pack structure when a second instance
   emerges (e.g. when a skillset needs a strategy pack beyond
   org-research)
4. Add doctrine tests for pack shape when the pack structure is
   codified

The second instance will likely emerge from skillset engineering
(`ns-*` skills) or from a skillset that needs domain-specific
research strategies. When it does, the pattern is documented and the
infrastructure path is clear.
