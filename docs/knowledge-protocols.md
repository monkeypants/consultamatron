# Knowledge Protocols

When a body of knowledge grows a use case that consumes it
structurally, a knowledge protocol emerges. The protocol defines
the contract between content and consumer. This article describes
the pattern, using the pantheon protocol and jedi council use case
as the running example.

## 1. The problem

A semantic pack stores knowledge as typed items in a directory with
a manifest. The [semantic pack convention](semantic-packs.md)
compresses, navigates, and describes that knowledge without caring
what the types mean. Pack-and-wrap sees `type: luminary` the same
way it sees `type: article` — both get a `_bytecode/` summary.

But some consumers do care what the types mean. A jedi council use
case does not want "any item" — it wants luminaries with specific
attributes: contribution to the field, invocation criteria, domain
relevance. A diagnostic use case does not want "any item" — it wants
anti-patterns with surface appeal, damage description, and diagnostic
triggers.

The gap between "typed item in a pack" and "item that a use case can
process structurally" is what a knowledge protocol fills.

## 2. Protocol = type + contract + use case

A knowledge protocol has three parts:

1. **Type**: the `type:` value in item frontmatter that identifies
   items belonging to this protocol (`luminary`, `pattern`,
   `anti-pattern`, `principle`)

2. **Contract**: the structural expectations that a use case has of
   items with this type. Not enforced by the pack convention — the
   use case defines and verifies the contract.

3. **Use case**: the `src/practice/` code that consumes items of this
   type for a specific purpose. No use case, no protocol — the items
   are just reference material.

The semantic pack convention provides the infrastructure (storage,
compression, manifest matching). The knowledge protocol provides the
semantics (what the items mean, how they are consumed, what
operations apply).

### Example: pantheon protocol

| Component | Pantheon |
|---|---|
| **Type** | `type: pantheon` in frontmatter |
| **Contract** | Each item describes a luminary: name, contribution, invocation trigger |
| **Use case** | Jedi council: select luminaries whose frameworks address the problem under analysis |

The jedi council use case reads `_bytecode/` summaries from a
pantheon pack, selects relevant luminaries based on the problem
domain, reads their full items, and invokes each perspective. The
selection step requires the contract — it needs to know what
"invocation trigger" means. Pack-and-wrap does not.

## 3. The promotion criterion

A topic becomes a protocol when a use case in `src/practice/` needs
to process items of that type structurally. This is the boundary
marker.

Before promotion, items are reference material. Agents browse them
through `_bytecode/` summaries. The `type:` field helps humans
organise the content. No code processes the type programmatically.

After promotion, a use case exists that:
- Filters items by type
- Reads item content with structural expectations
- Produces output that depends on the contract being satisfied

The promotion criterion is concrete and observable: does
`src/practice/` contain a use case that matches on this type? If
yes, protocol. If no, reference material with a type label.

### Example promotion path

1. An SWE skillset author writes `docs/pantheon.md` with luminary
   entries. Reference material — agents read it, but no code
   processes "luminary" as a concept.

2. The operator invokes a multi-perspective analysis during an
   engagement. The agent reads the pantheon, selects relevant
   luminaries, invokes each perspective. This works but is encoded
   in SKILL.md prose — the agent interprets "luminary" from context.

3. The pattern recurs. A jedi council use case is extracted into
   `src/practice/`. It reads items with `type: pantheon`, expects
   each to have invocation criteria, and selects based on engagement
   context. Pantheon is now a protocol.

Each step adds value independently. Step 1 is useful without step 3.
Step 3 formalises what step 2 was already doing informally.

## 4. Domain-generic protocols

Some protocols recur across consulting domains. The same structural
patterns appear in software engineering, Wardley Mapping, business
model analysis, and restaurant management — with different content.

| Protocol | Item type | Contract | Recurrence |
|---|---|---|---|
| **Pantheon** | `pantheon` | Luminary: contribution, invocation trigger | Any domain with authoritative thinkers |
| **Patterns** | `patterns` | Pattern: problem, solution, application trigger | Any domain with recurring solutions |
| **Principles** | `principles` | Principle: statement, provenance, application trigger | Any domain with design heuristics |
| **Anti-patterns** | `anti-patterns` | Anti-pattern: surface appeal, damage, diagnostic trigger | Any domain with recurring mistakes |

The SWE pantheon contains Beck, Larman, Fowler. A restaurant
management pantheon would contain Escoffier, Bocuse, David Chang.
Same protocol, different content. The jedi council use case works
with any pantheon because it matches on the contract, not on the
domain.

This is the Open/Closed Principle applied to knowledge: the protocol
is closed to modification (a pantheon item always has contribution
and invocation trigger); the content is open to extension (add
luminaries by adding markdown files).

## 5. Protocol-specific sub-protocols

Some protocols grow sub-protocols that apply only within their parent.
These are "peculiar sub-protocols" — they make sense for one protocol
but not for others.

### Example: notable works (peculiar to pantheon)

A luminary's notable works are a body of knowledge that only exists
in the context of the pantheon protocol. "Refactoring" is a notable
work of Martin Fowler. It does not make sense as a sub-protocol of
patterns or principles — it is anchored to a specific luminary.

```
pantheon/
├── index.md
├── martin-fowler.md
├── kent-beck.md
├── notable-works/          ← peculiar sub-protocol
│   ├── index.md
│   ├── refactoring.md
│   └── mythical-man-month.md
└── ...
```

The notable-works sub-protocol has its own contract: each item
describes a work (title, author, contribution, when to cite). A
use case that prepares citations or recommends reading would consume
this sub-protocol. Without that use case, notable works are just
reference material nested under pantheon.

### Cross-cutting sub-protocols

Some sub-protocols appear under multiple parent protocols but contain
different content in each. Criticism of a design pattern is different
knowledge from criticism of a luminary, even though both follow the
"criticism" sub-protocol structure.

```
pantheon/criticism/     → challenges to specific thinkers' ideas
patterns/criticism/     → arguments against pattern-heavy design
principles/criticism/   → cases where a principle was misapplied
```

These are not shared sub-protocols — they are independently authored
within their parent's scope. The parent's `_bytecode/` summarises
them. The criticism sub-protocol is a *use case pattern* (the same
interaction shape instantiated with different content), not a shared
data structure.

## 6. The jedi council: anatomy of a protocol use case

The jedi council is the first concrete knowledge protocol use case.
It demonstrates the full pattern.

### Inputs

- A **pantheon pack**: a semantic pack containing items with
  `type: pantheon`, each describing a luminary
- A **problem statement**: the technical or strategic question under
  analysis
- An **engagement context**: client, skillset, project stage

### Behaviour

1. Read `_bytecode/` summaries from the pantheon pack
2. Select luminaries whose invocation triggers match the problem
   domain (typically 5-7 from a larger pantheon)
3. Read full items for selected luminaries
4. For each luminary, analyse the problem through that luminary's
   framework (Beck applies Simple Design rules, Larman applies GRASP,
   Fowler applies refactoring heuristics, etc.)
5. Synthesise: where does the council agree, where does it diverge,
   what is the actionable recommendation?

### Contract requirements

The use case requires each pantheon item to contain:
- **Contribution**: what the luminary is known for (used for
  selection)
- **Invocation trigger**: when to invoke this perspective (used for
  matching against the problem statement)

Items that lack these cannot be meaningfully selected. The contract
is implicit in the item prose — it is not enforced by schema
validation. The use case trusts the content author to follow the
convention. If a luminary entry is a single line with no invocation
criteria, the jedi council will produce a shallow perspective.

### The protocol is the bridge

The semantic pack convention stores the luminaries. The jedi council
use case consumes them. The pantheon protocol is the bridge: it gives
the `type:` field meaning by defining the contract and the use case.

```
[semantic pack convention]     [knowledge protocol]      [use case]

  index.md                      type: pantheon            jedi council
  _bytecode/           →        contract: contribution,   selects luminaries
  items with type:              invocation trigger        invokes perspectives
  pack-and-wrap                                           synthesises
```

The convention is protocol-agnostic. The use case is
protocol-specific. The protocol connects them.

## 7. Protocols are not a type hierarchy

A jedi council analysis of this topic (applying Beck, Larman, Evans,
Liskov, Cockburn, Martin, Parnas) reached consensus on a critical
point: protocols are not subtypes of each other.

Code that processes a pantheon item cannot meaningfully process a
patterns item. They share a common convention (PackItem with name and
type) but not a common contract. A function that takes a generic
"protocol item" can only access the intersection of their contracts,
which is so thin it carries no useful behaviour.

The convention layer sees PackItem. The use case layer sees
domain-specific contracts. There is no intermediate layer. Encoding
a protocol taxonomy (root → core → peculiar) into `src/practice/`
entities would push protocol awareness into the convention layer,
violating the dependency rule and information hiding.

The correct architecture:

| Layer | Sees | Concern |
|---|---|---|
| **Convention** (inner) | PackItem: name, type | Storage, compression, manifest matching |
| **Use case** (middle) | Domain contracts: luminary, pattern, etc. | Selection, analysis, synthesis |
| **Adapter** (outer) | Markdown files with frontmatter | Reading files, populating contracts |

New protocols are added at the use case layer. The convention layer
never changes. This is OCP applied vertically through the
architecture.

## 8. When to build a protocol

Build a protocol when all three conditions hold:

1. **A recurring use case exists.** The same structured consumption
   pattern has appeared in multiple engagements or skills.

2. **The contract is concrete.** You can state what the use case
   expects from each item — not "some kind of knowledge" but
   "contribution, invocation trigger, domain relevance."

3. **The items already exist.** The content has been authored and
   iterated. The protocol formalises what the content already provides
   informally.

Do not build a protocol speculatively. If only one skill reads the
content, and it does so by browsing `_bytecode/` summaries without
structural expectations, no protocol is needed. The content is
reference material. It serves its purpose. The protocol will emerge
when the second use case arrives and the common contract becomes
visible.

This is interface discovery applied to knowledge: discover the
protocol from concrete need, not from speculative design.

## 9. Relationship to other articles

- [Semantic Packs](semantic-packs.md) defines the content convention
  that knowledge protocols build on. Protocols require semantic packs;
  semantic packs do not require protocols.

- [Engagement Protocol](engagement-protocol.md) defines the use case
  layer that orchestrates skillset pipelines. Knowledge protocols are
  consumed within this orchestration — the jedi council might be
  invoked as part of an engagement's analysis stage.

- Issue #100 proposes the pantheon/jedi council as the first concrete
  knowledge protocol implementation.

- Issue #98 proposes the KnowledgePack entity model and PackItem
  protocol — the convention-layer infrastructure that knowledge
  protocols build on.

## 10. Current state

**What exists today:**
- `personal/swe/docs/` contains four protocol item types (pantheon,
  patterns, principles, anti-patterns) as flat files in a semantic
  pack with a manifest
- The jedi council pattern has been exercised informally — luminaries
  are invoked during design sessions by reading the pantheon and
  applying each framework
- No `src/practice/` use case processes protocol types structurally

**What emerges next:**
- The jedi council use case is extracted into `src/practice/` when
  multi-perspective analysis recurs across engagements (#100)
- A diagnostic use case emerges when anti-pattern matching becomes
  a structured skill step
- Each extraction follows the promotion path: informal use →
  recurring pattern → extracted use case → formalised protocol

The protocols will declare themselves through concrete need. The
semantic pack convention is ready to support them whenever they
arrive.
