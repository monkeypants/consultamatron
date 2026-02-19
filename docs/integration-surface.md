---
type: article
title: The Integration Surface
description: >
  What a Skillset Capability is, why the practice/skillset boundary
  decomposes into typed ports, and how the Consultamatron Integration
  Protocol composes from independent facets.
related:
  - capabilities/index.md
  - context-mapping-the-integration-surface.md
  - articles/language-port-testing.md
  - articles/capability-token-economics.md
  - articles/engagement-protocol.md
  - semantic-waist.md
---

# The Integration Surface

The practice layer is a platform. Skillsets are plugins. The boundary
between them is the integration surface — the collection of contracts
that a skillset must satisfy to participate in the Consultamatron
engagement protocol.

This article names the pattern, explains why the boundary decomposes
into independent facets, and describes the Capability entity that
makes the decomposition explicit.

## The pattern

Consultamatron follows hexagonal architecture (Cockburn). The practice
layer defines ports — typed contracts for the services it needs. Skillsets
supply adapters — domain-specific implementations that satisfy those
contracts. The practice layer orchestrates engagements without knowing
whether a skillset implements wardley mapping, business model canvases,
or restaurant management.

The integration surface is not one contract. It is twelve (and counting).
Each contract governs a different aspect of how practice and skillset
interact:

- How the skillset declares its pipeline stages
- How gate artifacts are stored and inspected
- How workspace artifacts become deliverable content
- How domain-specific services are registered
- How knowledge is packaged and discovered
- How luminaries and vocabulary are supplied for analysis
- How research strategies are described
- How the concept space is structured for operator learning

Each of these is a **Skillset Capability** — one facet of the
**Consultamatron Integration Protocol**.

## Why facets, not a monolithic contract

A monolithic skillset interface would violate Interface Segregation
(Martin). A pipeline-only skillset should not need to satisfy a knowledge
protocol contract. A knowledge-only pack should not need to declare
pipeline stages.

Facets decompose the surface by the Parnas criterion: each facet
encapsulates one design decision that varies independently across
skillsets. Pipeline structure varies independently from knowledge
structure. Gate format varies independently from research strategy.
Presenter assembly varies independently from pedagogic metadata.

The practice layer's code follows this decomposition. Use cases that
orchestrate engagements depend on pipeline declarations and gate
inspection. Use cases that render deliverables depend on presenters.
Use cases that run the jedi council depend on knowledge protocols. No
use case depends on the entire surface.

## Two mechanisms

Capabilities use one of two enforcement mechanisms:

**Code ports** are Python Protocol classes. The skillset implements the
protocol in Python; the DI container wires it at startup; conformance
tests verify it in CI. Code ports cost zero tokens, fail at import time
if violated, and are structurally enforced by `pytest -m doctrine`.
Pipeline declaration, gate inspection, deliverable presentation, service
registration, and conformance testing are code ports.

**Language ports** are filesystem conventions with documented structural
contracts. The skillset supplies markdown files in agreed formats; skills
and use cases read them by convention. Language ports cost tokens to
verify — the verification itself is a language task. Knowledge packs,
knowledge protocols, research strategies, analysis, and pedagogic
metadata are language ports.

The mechanism is not a quality judgement. Code ports enforce what can
be enforced by code. Language ports serve contracts that are inherently
about content structure and meaning — things code cannot evaluate without
becoming an LLM.

Two capabilities (iteration evidence, voices) have no defined mechanism
yet. They are real integration facets observed in practice, documented
so that their contracts crystallise through use rather than speculation.

## The Capability entity

Each capability is described by a `Capability` entity
(`src/practice/entities.py`) with these properties:

| Property | Purpose |
|---|---|
| `name` | Canonical identifier |
| `description` | What the capability does |
| `direction` | Who drives the interaction (driver/driven) |
| `mechanism` | How the contract is enforced (code_port/language_port) |
| `adapter_contract` | What the skillset must supply |
| `discovery` | How the practice layer finds the adapter |
| `maturity` | How far enforcement has progressed |
| `hidden_decision` | What design decision this capability encapsulates (Parnas) |
| `information_expert` | Who fills each side of the boundary (Larman) |
| `structural_tests` | Which doctrine tests verify this capability |
| `semantic_verification` | Token-burning verification spec for language ports |

The frontmatter of each capability file in `docs/capabilities/` matches
this entity. The knowledge pack is simultaneously documentation (for
humans) and a structured evaluation surface (for rs-assess).

## Direction

All twelve current capabilities are **driven**: the practice layer reaches
into the skillset and reads what it finds. The skillset is passive —
it declares, the practice layer discovers and consumes.

The reverse direction exists conceptually. The operator drives the
practice layer through the CLI (the driver port in hexagonal terms).
But no capability currently formalises a contract where the skillset
drives practice. If one emerges, the entity supports it.

## Maturity

Capabilities are not born fully enforced. They progress through three
levels:

**Nascent**: the contract is documented in a capability file but has no
structural enforcement. The contract exists as shared understanding
between contributors. Most language port capabilities start here.

**Established**: structural tests exist for at least some aspects of
the contract. The capability is discoverable through a defined mechanism.
Convention is documented and followed, but coverage is incomplete.

**Mature**: full structural tests run in CI, and semantic verification
is defined (even if token-burning verification is triggered manually
rather than on every commit). The capability is fully enforced — the
correct path is the only path that passes.

The maturity gradient is the platform's path from "we document
conventions" to "we structurally enforce them." Each capability
progresses independently.

## The hidden decision / information expert pair

Every capability file records two architectural properties:

**Hidden decision** (Parnas): what design decision this capability
encapsulates. Pipeline declaration hides the methodology's stage
sequence. Knowledge packs hide the domain's knowledge structure.
Research strategies hide what questions a domain needs answered.

**Information expert** (Larman): who has the knowledge to fill each
side. The skillset author is the information expert for adapter content
(they know the methodology). The practice layer is the information
expert for consumption machinery (it knows the engagement protocol).

These two properties are complementary. Parnas says where to draw the
boundary (encapsulate what varies). Larman says who fills each side
(assign to the party with the knowledge). Together they explain both
the structure and the responsibility assignment of each capability.

## Discovery

Each capability uses one of four discovery mechanisms:

- **DI scan**: practice layer scans registered bounded contexts at
  startup and finds Python Protocol implementations
- **Filesystem convention**: practice layer looks for files at
  conventional paths within the skillset package
- **Pack manifest**: practice layer reads a knowledge pack's `index.md`
  to discover typed items
- **Not defined**: capability is documented but the practice layer has
  no automated discovery mechanism

Discovery mechanisms do not require the practice layer to know which
skillsets exist in advance. A new skillset that satisfies the conventions
is discovered automatically — the Open/Closed Principle (Martin) applied
to the integration surface.

## Shared kernels follow the pack convention

At every level of the hierarchy, a context provides a knowledge pack
directory that its child contexts consume as a shared kernel:

| Level | Shared kernel | Producer | Consumers |
|---|---|---|---|
| Practice | `docs/` | practice development | all skillsets (design time) |
| Skillset | `{skillset}/docs/` | ns-implement | all skills in that skillset |
| Client | `clients/{org}/resources/` | org-research | all engagements for that client |
| Engagement | `{engagement}/resources/` | engagement-scoped research | all projects in that engagement |

The pattern: **a parent context's knowledge pack directory is the shared
kernel for its children.** Every shared kernel listed above is produced
by a research-like activity, follows the semantic pack convention
(`index.md` manifest, typed items, optional `_bytecode/` mirror), and
is immutable after agreement.

This is not a separate convention from knowledge packs. It is knowledge
packs applied structurally: the pack convention already defines how
knowledge is stored and discovered; the shared kernel convention says
where in the hierarchy a pack sits and who depends on it. Conformance
tests that verify pack shape (`doctrine_pack_shape`) transitively verify
shared kernel structure.

The convention has a diagnostic use. When integration friction involves
two sibling contexts needing different things from the same shared data,
the shared kernel is too large. The remedy (per Evans) is to narrow the
kernel and move context-specific translation into per-context
anti-corruption layers — which in this architecture means per-skillset
research skills.

## What this is not

This is not a framework. A skillset author does not inherit from a base
class, call a registration API, or conform to a template. They declare
pipeline stages as data, supply knowledge as files, implement protocols
as methods. The integration surface is a set of contracts, not a set of
calls into framework code.

This is not speculative architecture. Every capability in the catalogue
was identified from existing practice — observed at the boundary, then
named and documented. Capabilities that lack a mechanism (iteration
evidence, voices) are documented as nascent rather than designed
prematurely.

## References

- [Capabilities Pack](capabilities/index.md) — the full catalogue of
  twelve capabilities with structured frontmatter
- [Context Mapping the Integration Surface](context-mapping-the-integration-surface.md) —
  DDD analysis of the practice/skillset boundary
- [Language Port Testing](articles/language-port-testing.md) — verification
  strategy for non-code adapters
- [Capability Token Economics](articles/capability-token-economics.md) —
  scaling rules for token-burning verification
- [Engagement Protocol](articles/engagement-protocol.md) — the hexagonal
  architecture that the integration surface sits within
- [Semantic Waist](semantic-waist.md) — the typed data layer between
  engagement orchestration and skillset execution
- [Knowledge Protocols](articles/knowledge-protocols.md) — how typed
  knowledge items become use-case-consumable contracts
