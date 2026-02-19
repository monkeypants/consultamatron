---
type: capability
name: knowledge-packs
description: >
  Practice provides dual-audience knowledge management through the
  semantic pack convention. Skillsets supply typed items with manifests
  that serve both human readers (prose) and agent consumers (bytecode).
direction: driven
mechanism: language_port
adapter_contract: >
  A directory containing index.md with YAML manifest frontmatter (name,
  purpose, actor_goals, triggers). Item files with type: frontmatter
  and prose bodies. Optionally a summary.md (human-authored synthesis)
  and _bytecode/ directory mirroring items with generated summaries.
  Design-time packs live in BC source directories; runtime packs live
  in client workspaces.
discovery: pack_manifest
maturity: established
hidden_decision: >
  What bodies of knowledge a domain contains and how they are
  structured internally. The practice layer sees packs through
  the convention (manifest, items, bytecode). It does not know whether
  a pack contains luminaries, patterns, research reports, or recipes.
information_expert: >
  The skillset author for design-time packs (domain reference material).
  The engagement execution agent for runtime packs (client-specific
  findings). Both follow the same convention.
structural_tests:
  - doctrine_pack_shape
semantic_verification:
  reference_problem: >
    Navigate this knowledge pack: read the manifest, select the most
    relevant item for a general architecture question, read it, and
    summarise the value it provides.
  sample_size: 3
  max_tokens_per_evaluation: 2000
  evaluation_criteria:
    - manifest actor_goals identify concrete actors with actionable goals
    - triggers describe situations an agent can match against
    - items have type frontmatter and substantive prose bodies
    - _bytecode/ summaries (if present) enable selection without reading full items
  trigger: content change in pack items or manifest
---

# Knowledge Packs

Knowledge packs are the dual-audience knowledge infrastructure.
Every body of methodology reference material — luminaries, patterns,
principles, research strategies — is stored as a semantic pack that
both humans and agents can navigate efficiently.

## What the practice layer provides

The semantic pack convention: `index.md` manifests with self-describing
frontmatter, `type:` frontmatter on items for protocol-level filtering,
and `_bytecode/` mirrors for token-efficient progressive disclosure.
Pack-and-wrap compiles `_bytecode/` summaries from item bodies.

Two access paths to the same knowledge:
- **Human path**: `summary.md` → item bodies (prose, citations, narrative)
- **Agent path**: `_bytecode/` mirror (compressed summaries, navigable
  without reading full items)

## What the skillset supplies

Directories of markdown files following the convention. Design-time
packs supply domain-generic methodology references (pantheon, patterns,
principles, anti-patterns, research strategies). Runtime packs supply
client-specific engagement findings (research reports, analysis outputs).

The `type:` field on items is the bridge to knowledge protocols. The
pack convention stores the type. Knowledge protocol use cases give it
meaning. A pack can contain items of types that no use case processes
yet — they are reference material waiting for a use case to promote
them to protocol status.

## Architectural rationale

The semantic pack convention is the Open Host Service (Evans) for
knowledge. Any use case can consume any pack through the convention
without the pack knowing about the consumer. The convention is
protocol-agnostic: pack-and-wrap compresses a pantheon item the same
way it compresses a research report.

OCP applied at two levels: pack content is open to extension (add a
markdown file); pack consumption is open to extension (write a new
use case that reads existing packs). The convention itself is closed
to modification.

## Verification

Shape verification (Tier 0): `index.md` exists with valid manifest
YAML, items have `type:` frontmatter. This is a zero-token doctrine
test.

Contract verification (Tier 1, token-conservative): manifest
`actor_goals` and `triggers` are actionable, items have substantive
bodies, `_bytecode/` is not stale. This burns tokens but evaluates
structure, not quality.

Fitness evaluation (Tier 2, token-generous): the pack serves its
declared actor-goals effectively. An agent can navigate from manifest
to relevant item using `_bytecode/` summaries alone. This is the
full progressive disclosure test.

## References

- [Semantic Packs](../articles/semantic-packs.md) — the convention
  definition
- [Knowledge Protocols](../articles/knowledge-protocols.md) — how
  use cases consume typed items
