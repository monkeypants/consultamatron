---
type: capability
name: pedagogic-metadata
description: >
  Practice provides graduation gradient detection and wetware efficiency
  calibration. Skillsets supply their domain's concept space through
  the docs/ knowledge pack convention — the bytecode tree is the
  machine-navigable knowledge structure, the items are the concepts,
  and the nesting encodes learning dependencies.
direction: driven
mechanism: language_port
adapter_contract: >
  A docs/ directory following the semantic pack convention. The pack's
  _bytecode/ tree is the concept catalogue — each summary represents a
  concept the operator may encounter. Nesting encodes dependency
  structure (a nested pack requires understanding its parent). The
  manifest's actor_goals describe who learns what. Protocol item types
  (pantheon, patterns, principles, anti-patterns) partition the concept
  space by function. The docs/ pack is both reference material and
  pedagogic structure simultaneously.
discovery: pack_manifest
maturity: nascent
hidden_decision: >
  What concepts an operator needs to learn to be effective in a domain,
  and how those concepts relate to each other. The practice layer
  detects fluency and calibrates scaffolding. The skillset's docs/
  pack embodies the concept space through its structure.
information_expert: >
  Split. The skillset's docs/ pack knows what to teach (its items are
  the concepts, its structure is the dependency graph). The practice
  layer knows when and how much to teach (detecting fluency from
  negotiation resolution, calibrating scaffolding intensity).
structural_tests: []
semantic_verification:
  reference_problem: >
    Navigate the docs/ pack's _bytecode/ tree. Can an agent identify
    which concepts a novice operator would need explained when
    encountering a stage-2 proposal for the first time? Does the pack
    structure support progressive disclosure of the concept space?
  sample_size: 3
  max_tokens_per_evaluation: 2000
  evaluation_criteria:
    - docs/ follows the semantic pack convention (index.md, type frontmatter, items)
    - _bytecode/ tree is navigable as a concept catalogue
    - nesting reflects conceptual dependency (foundational concepts at higher levels)
    - manifest actor_goals identify learning audiences
  trigger: structural change in docs/ pack (new items, reorganisation)
---

# Pedagogic Metadata

The pedagogic metadata capability reuses the docs/ knowledge pack
convention. A skillset's docs/ pack is simultaneously reference
material (what the domain knows) and pedagogic structure (what the
operator needs to learn). The `_bytecode/` tree is the concept
catalogue; the items are the concepts; the nesting is the dependency
graph.

## What the practice layer provides

The graduation gradient: detect operator fluency from negotiation
resolution quality. Low-resolution feedback indicates low fluency —
increase pedagogic scaffolding. High-resolution feedback indicates
high fluency — reduce scaffolding to conclusions and evidence.

Three pedagogic affordances in output design:
- **Make reasoning visible** — conclusion first, then reasoning chain
- **Name the concepts** — use canonical vocabulary from the docs/ pack
- **Show the evidence chain** — connect findings to pack items the
  operator can follow up on

The practice layer calibrates these affordances based on observed
fluency. The docs/ pack tells it *what* concepts to scaffold; the
operator's negotiation behaviour tells it *how much* to scaffold.

## What the skillset supplies

A `docs/` directory following the semantic pack convention. The SWE
skillset's `docs/` pack currently contains four protocol item types:
`pantheon.md`, `patterns.md`, `principles.md`, `anti-patterns.md`.
These are the concept space of software engineering consulting —
partitioned by function (who to consult, what solutions exist, what
heuristics apply, what to avoid).

The `_bytecode/` tree mirrors this structure with compressed summaries.
An agent navigating `_bytecode/` encounters the concept space at
summary resolution — enough to decide which concepts are relevant to
the current interaction, without loading full item content.

Pack nesting encodes learning dependency. If `patterns/` were promoted
to a directory pack with `strategy.md`, `structure.md`, `behavioral.md`
subdirectories, the nesting would encode: understanding strategy
patterns requires understanding patterns generally. The `_bytecode/`
tree at each level provides the progressive disclosure mechanism.

## The docs/ pack is the adapter

This is not a new convention. It is the recognition that the existing
docs/ knowledge pack convention already serves the pedagogic metadata
role:

| Pedagogic need | Served by |
|---|---|
| Concept catalogue | Items in the docs/ pack |
| Concept dependencies | Nesting structure of the pack |
| Machine-navigable concept space | `_bytecode/` tree |
| Learning audiences | Manifest `actor_goals` |
| Concept activation conditions | Manifest `triggers` |
| Progressive disclosure | `_bytecode/` → item → nested pack |

What does not yet exist is the practice-layer machinery that *consumes*
this structure pedagogically — the graduation gradient that reads the
concept space and calibrates output accordingly. The adapter is ahead
of the port.

## Architectural rationale

Pedagogy as compounding investment: the operator learns across
engagements; the LLM does not. Every unit of understanding built in the
operator is a permanent improvement to dyad capability. The docs/ pack
is the compounding instrument — it grows as the skillset matures, and
its `_bytecode/` tree becomes a richer concept map for pedagogic
calibration.

The split information expert is resolved by the convention: the
skillset knows what to teach (its docs/ pack is the concept space),
the practice layer knows when and how much to teach (it observes the
operator). The docs/ pack bridges the gap without requiring a separate
pedagogic metadata format.

## References

- [Wetware Efficiency](../wetware-efficiency.md) — operator cognition
  as scarce resource, graduation gradient, pedagogy as investment
- [Semantic Packs](../articles/semantic-packs.md) — the convention that
  docs/ packs follow
- [Voices Protocol](../articles/voices-protocol.md) — alternate
  delivery channels calibrated to cognitive style
