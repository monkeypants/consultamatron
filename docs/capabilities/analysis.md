---
type: capability
name: analysis
description: >
  Practice provides multi-perspective analytical synthesis through the
  jedi council use case. Skillsets supply luminaries (pantheon items)
  and domain vocabulary (patterns, principles, anti-patterns) that the
  council draws on to analyse problems through established frameworks.
direction: driven
mechanism: language_port
adapter_contract: >
  A pantheon.md file (or pantheon/ knowledge pack) with type: pantheon
  frontmatter. Each luminary entry is an H2 section containing: a
  contribution description (what they are known for, used for selection),
  an invocation trigger sentence starting with "Invoke when..." (when to
  invoke this perspective, used for matching against the problem
  statement). Supporting vocabulary in patterns.md, principles.md, and
  anti-patterns.md files with their respective type: frontmatter.
discovery: pack_manifest
maturity: nascent
hidden_decision: >
  Who the authoritative thinkers are in a domain, what frameworks they
  contribute, and when each perspective is relevant. The practice layer
  synthesises perspectives and produces deliberations. It does not know
  whether the domain's luminaries are software engineers, chefs, or
  economists.
information_expert: >
  The skillset author. They know the domain's intellectual tradition —
  its luminaries, their contributions, and the situations where each
  framework applies. The practice layer knows how to orchestrate
  multi-perspective analysis; the skillset knows whose perspectives
  to orchestrate.
structural_tests: []
semantic_verification:
  reference_problem: >
    Select 3 luminaries from the pantheon. For each, evaluate: does the
    contribution description distinguish this luminary from others? Does
    the invocation trigger identify a concrete problem type? Would the
    jedi council produce a non-generic perspective from this entry?
  sample_size: 3
  max_tokens_per_evaluation: 2000
  evaluation_criteria:
    - each luminary has a contribution description
    - each luminary has an invocation trigger that identifies concrete problem types
    - luminaries are distinguishable (different frameworks, different triggers)
    - the council would produce distinct perspectives, not generic advice
  trigger: content change in pantheon or vocabulary files
---

# Analysis (Jedi Council)

The analysis capability makes luminaries into analytical instruments.
Without it, a pantheon is reference material. With it, luminaries are
invoked to analyse the operator's specific problem through their
specific frameworks.

## What the practice layer provides

The jedi council use case (designed, not yet implemented as code):

1. **Scope resolution** — the operator names a subject (artifact, project,
   engagement, client); the system resolves it to a scope level and loads
   appropriate context
2. **Knowledge resolution** — reads `_bytecode/` summaries from the
   subject's skillset pantheon, selects 5-7 luminaries whose invocation
   triggers match the problem domain
3. **Perspective invocation** — reads full items for selected luminaries,
   analyses the subject through each luminary's framework
4. **Synthesis** — identifies consensus, names divergence, proposes
   actionable recommendation
5. **Citation** — every framework, pattern, principle cited with its
   location in the knowledge pack

The output is a deliberation with per-luminary sections, synthesis, and
a council sources table. The sources table is the pedagogic mechanism:
operators accumulate domain vocabulary by seeing named concepts applied
to their own work.

## What the skillset supplies

A `type: pantheon` pack item containing luminary entries. Each entry
describes one authoritative thinker in the domain: their contribution
to the field and the situations where their perspective is most
relevant. The SWE pantheon contains 16 luminaries (Beck, Larman,
Cockburn, Fowler, Martin, Liskov, Brooks, Parnas, Dijkstra, Cunningham,
Anthropic, Evans, Feathers, DeMarco, Hohpe, Weinberg). A restaurant
management pantheon would contain Escoffier, Bocuse, David Chang. Same
protocol, different content.

Supporting vocabulary — patterns, principles, anti-patterns — is
available as reference during analysis. Each luminary perspective draws
on whichever domain vocabulary is relevant. The vocabulary items are
not pre-selected; they are cited by name during perspective invocation.

## The token efficiency mechanism

The two-path access model is critical for the jedi council. Reading
all 16 luminaries in full costs thousands of tokens. Reading
`_bytecode/` summaries costs hundreds. The council reads summaries
to select 5-7 relevant luminaries, then reads full items only for
those selected. 16 compressed to summaries, 5-7 expanded to full
items — progressive disclosure applied to analytical selection.

## Verification

No structural tests exist yet. The pantheon contract (contribution +
invocation trigger) is documented but not enforced. Shape tests would
verify: `type: pantheon` frontmatter, H2 sections present, minimum
luminary count. Contract verification (token-burning) would evaluate
whether invocation triggers are specific enough for the council to
produce distinct perspectives.

## References

- [Jedi Council](../articles/needs-jedi-council.md) — the use case
  specification
- [Knowledge Protocols](../articles/knowledge-protocols.md) — the
  pantheon protocol as the running example
- [Voices Protocol](../articles/voices-protocol.md) — a live
  deliberation demonstrating the council in action
