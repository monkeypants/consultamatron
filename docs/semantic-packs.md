# Semantic Packs

A general-purpose content convention for managing bodies of knowledge
at dual fidelity. Any directory of markdown files becomes a knowledge
pack when it gets a manifest. The convention is protocol-agnostic — it
knows how to store, describe, and compress knowledge, not how
knowledge is consumed.

## 1. The convention

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

The convention places type on items so that domain-specific use cases
can match on it. But the convention itself does not define what types
mean — that is the concern of knowledge protocols (see
[Knowledge Protocols](knowledge-protocols.md)).

## 3. Topic and protocol: separate concerns

Every node in a knowledge tree has two orthogonal properties:

- **Topic**: what the knowledge is about (software engineering,
  restaurant management, Wardley Mapping)
- **Protocol**: what shape the knowledge takes and what use case
  consumes it (pantheon, patterns, principles)

The semantic pack convention operates on topics. It stores, compresses,
and navigates knowledge regardless of protocol. A pack of design
patterns and a pack of restaurant health codes use the same convention
— `index.md`, items with `type:` frontmatter, `_bytecode/` mirror.

Protocols are a use-case-layer concern. When a body of knowledge grows
a use case that consumes items structurally (a jedi council selecting
luminaries, a diagnostic skill matching anti-patterns), a protocol
emerges. The protocol defines the contract between content and
consumer. See [Knowledge Protocols](knowledge-protocols.md) for the
full treatment.

The convention supports protocols through the `type:` field in item
frontmatter. Pack-and-wrap compiles `_bytecode/` regardless of type.
Use cases filter by type when they need to. The convention is closed;
protocols are open to extension.

## 4. Progressive disclosure through nesting

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

### Promotion path

A flat file that grows large can be promoted to a directory:

1. `patterns.md` (flat, 40 patterns) → `patterns/index.md` + one
   file per pattern clustered into subdirectories
2. Pack-and-wrap recompiles `_bytecode/` at the parent level
3. Nothing else changes — the parent manifest still routes to the
   same topic

The growth path is: flat file → directory with items → directory
with clustered subdirectories. Each step is an independent promotion
that recompiles one level of `_bytecode/`.

## 5. The pack-and-wrap operation

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
compilation step (writing to `_bytecode/`) is mechanical. A pack is
**clean** when every item's `_bytecode/` mirror is newer than the item
itself, **dirty** when at least one item is newer than its mirror, and
the compilation is **absent** when no `_bytecode/` directory exists.
These three states are represented by `CompilationState` in
`practice.entities`.

Pack-and-wrap is protocol-agnostic. It compresses any item regardless
of type. Protocol-aware operations (selecting luminaries, matching
anti-patterns) are use case concerns, not pack-and-wrap concerns.

### Incremental adoption

Any existing directory of markdown files can become a knowledge pack
incrementally:

1. Add `index.md` with manifest frontmatter → directory is a pack
2. Add `type:` frontmatter to existing files → items are typed
3. Run pack-and-wrap → `_bytecode/` generated with summaries

Each step adds value independently. Step 1 alone is enough for an
agent to decide "should I look in here?"

## 6. The manifest

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

## 7. The PackItem protocol

Items declare their type in frontmatter. The infrastructure protocol
is defined in `practice.entities`:

```python
class PackItem(Protocol):
    """Any item in a knowledge pack."""
    name: str
    item_type: str

class CompilationState(str, Enum):
    CLEAN = "clean"   # bytecode newer than all items
    DIRTY = "dirty"   # at least one item newer than its mirror
    ABSENT = "absent"  # no _bytecode/ directory
```

Name is derived from the filename. Type is the frontmatter `type:`
field. This is the narrow interface between the convention layer and
the use case layer.

Pack-and-wrap sees PackItem. It does not need to know what the types
mean. Use cases see domain-specific types (luminary, pattern,
anti-pattern) by reading the `item_type` field and applying their own
contract. The convention is closed to modification; domain-specific
types are open to extension.

## 8. Two lifecycle contexts

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

## 9. The Open/Closed Principle applied

The semantic pack convention embodies OCP at two levels.

### Pack content is open to extension

Adding a new item means adding a markdown file with `type:` frontmatter
and re-running pack-and-wrap to generate its `_bytecode/` summary. No
code changes. No SKILL.md modifications.

### Pack consumption is open to extension

New use cases can consume existing packs without modifying the pack
or the pack-and-wrap use case. A research strategy pack authored for
`wm-research` can be consumed by a hypothetical `scenario-planning`
skill — it reads the same `_bytecode/` through a different adapter.

The core defines the pack convention (closed). Skills and use cases
define how they consume packs (open). Knowledge protocols define what
types mean (open). See [Knowledge Protocols](knowledge-protocols.md)
for the consumption side of this contract.

## 10. Structural enforcement

### Doctrine test: pack shape

A conformance test can verify that every semantic pack has the
required structure: `index.md` exists with valid manifest frontmatter,
items have `type:` frontmatter. Same pattern as pipeline coherence
and gate consumes tests.

### Doctrine test: compilation freshness

A conformance test can verify that no pack is dirty: if any item is
newer than its `_bytecode/` mirror, the pack's `CompilationState` is
`DIRTY` and it needs recompilation. Absent packs (no `_bytecode/`
directory) may be acceptable for newly created packs that have not
yet been compiled. This catches the case where a skill author adds
content but forgets to re-run pack-and-wrap.

These tests apply uniformly to both runtime and design-time packs.
The test fixture discovers packs by the presence of `index.md` with
manifest frontmatter, not by hard-coded paths. The tests are
protocol-agnostic — they verify the convention, not the content.

## 11. Current state and next steps

The pattern exists implicitly in org-research output and in the SWE
skillset docs. It has not been extracted as a named concept with
structural enforcement.

**What exists today:**
- org-research produces research with reports, summary, and index —
  but compression is encoded in SKILL.md prose, not in a protocol
  or use case
- `personal/swe/docs/` is a design-time pack with manifest, four
  protocol item types (pantheon, patterns, principles, anti-patterns),
  and no `_bytecode/` yet
- `docs/` is a half-formed design-time pack: articles and conventions
  about the platform, consumed by skill authors, contributors, and
  human/AI dyads
- `KnowledgePack`, `ActorGoal`, `PackItem`, and `CompilationState`
  are defined in `practice.entities` (#98) with round-trip conformance
  tests

**What this article proposes:**
1. Name the convention (done — this article)
2. Implement pack-and-wrap use cases, test on `docs/` (#99)
3. Build knowledge protocols as use cases emerge (see
   [Knowledge Protocols](knowledge-protocols.md))
4. Extract design-time packs when skillsets need them

Any directory of markdown files becomes a knowledge pack the moment
it gets an `index.md` with manifest frontmatter and its files get
`type:` frontmatter. Pack-and-wrap compiles `_bytecode/` summaries.
Agents navigate `_bytecode/` for cheap progressive disclosure, read
full items only when needed. What the types *mean* — which use cases
consume them and how — is a separate concern.
