---
type: capability
name: knowledge-protocols
description: >
  Practice provides use cases that consume typed knowledge items
  structurally. Skillsets supply items satisfying protocol contracts —
  the bridge between the convention layer (storage) and the use case
  layer (domain-specific consumption).
direction: driven
mechanism: language_port
adapter_contract: >
  Items with type: frontmatter matching the protocol type (pantheon,
  patterns, principles, anti-patterns). Each item's prose body satisfies
  the protocol's structural contract. The contract is protocol-specific:
  pantheon items need contribution and invocation trigger; pattern items
  need problem, solution, and application trigger; anti-pattern items
  need surface appeal, damage, and diagnostic trigger.
discovery: pack_manifest
maturity: nascent
hidden_decision: >
  What the protocol types mean — the semantic contract between content
  and consumer. The convention layer sees type: pantheon as a label.
  The knowledge protocol layer sees it as a contract requiring
  contribution descriptions and invocation triggers.
information_expert: >
  The skillset author for content authoring (they know the domain's
  luminaries, patterns, principles). The use case for contract definition
  (it knows what structural elements it needs to function).
structural_tests: []
semantic_verification:
  reference_problem: >
    Select 3 items of the declared protocol type. Evaluate whether each
    satisfies the protocol contract: does a pantheon item have a
    contribution and invocation trigger? Does a pattern item have
    problem, solution, and application trigger?
  sample_size: 3
  max_tokens_per_evaluation: 2000
  evaluation_criteria:
    - items are typed with valid protocol type in frontmatter
    - each item satisfies the structural contract for its type
    - contract elements are specific enough for the use case to act on
    - invocation triggers distinguish this item from others of the same type
  trigger: content change in protocol items
---

# Knowledge Protocols

A knowledge protocol emerges when a use case in the practice layer needs
to process items of a particular type structurally. The protocol is the
bridge between "typed item in a pack" and "item a use case can consume."

## What the practice layer provides

Use cases that filter items by type, read content with structural
expectations, and produce output dependent on the contract being
satisfied. The jedi council is the first concrete knowledge protocol
use case — it selects luminaries from a pantheon pack and invokes each
perspective.

The protocol defines a three-layer architecture:

| Layer | Sees | Concern |
|---|---|---|
| Convention (inner) | PackItem: name, type | Storage, compression, manifest |
| Use case (middle) | Domain contracts | Selection, analysis, synthesis |
| Adapter (outer) | Markdown with frontmatter | Reading files, populating contracts |

New protocols are added at the use case layer. The convention layer
never changes. OCP applied vertically through the architecture.

## What the skillset supplies

Items whose prose bodies satisfy the protocol contract. The contract is
implicit in the item prose — the use case trusts the content author to
follow the convention. Four domain-generic protocols recur across
consulting domains:

| Protocol | Contract | Use case |
|---|---|---|
| Pantheon | Contribution, invocation trigger | Jedi council selects luminaries |
| Patterns | Problem, solution, application trigger | Target structure selection |
| Principles | Statement, provenance, application trigger | Evaluating structure, justifying decisions |
| Anti-patterns | Surface appeal, damage, diagnostic trigger | Diagnosing code smells, naming problems |

The same four protocols apply to any consulting domain — SWE, restaurant
management, supply chain — with different content. The jedi council
works with any pantheon because it matches on the contract, not the
domain.

## The promotion criterion

A topic becomes a protocol when a use case in the practice layer needs
to process items of that type structurally. Before promotion, items are
reference material. After promotion, a use case exists that filters by
type, reads with expectations, and depends on the contract.

The criterion is concrete: does the practice layer contain a use case
that matches on this type? If yes, protocol. If no, reference material
with a type label.

## Verification

No structural tests exist yet. The protocol contracts are documented
in articles but not enforced. Token-burning verification during
skillset engineering evaluates whether items satisfy their protocol
contracts — contribution descriptions are specific, invocation triggers
are actionable, contract elements are present.

This is the nascent maturity stage. Promotion to established requires
shape tests that verify typed items have the minimum structural elements
their protocol demands.

## References

- [Knowledge Protocols](../articles/knowledge-protocols.md) — the full
  treatment of protocol = type + contract + use case
- [Semantic Packs](../articles/semantic-packs.md) — the convention layer
  that protocols build on
- [Jedi Council](../articles/needs-jedi-council.md) — the first concrete
  protocol use case
