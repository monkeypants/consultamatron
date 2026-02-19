---
type: article
title: Context Mapping the Integration Surface
description: >
  DDD context map analysis of the practice/skillset boundary. How the
  eight strategic DDD relationships manifest in the Consultamatron
  Integration Protocol and what that reveals about the architecture.
related:
  - integration-surface.md
  - capabilities/index.md
  - engagement-protocol.md
  - semantic-waist.md
  - articles/knowledge-protocols.md
---

# Context Mapping the Integration Surface

The integration surface is a hexagonal architecture boundary. This article
analyses the same boundary through the DDD context mapping lens (Evans).
The two perspectives are complementary: hexagonal architecture describes
the shape (ports and adapters); context mapping describes the
relationships (how bounded contexts negotiate their shared territory).

## The bounded contexts

Consultamatron has one platform context and multiple domain contexts:

**Practice layer** (platform context): engagement orchestration, pipeline
tracking, deliverable rendering, conformance testing, CLI routing. This is
the domain-agnostic machinery that makes consulting engagements work
regardless of methodology.

**Skillset bounded contexts** (domain contexts): wardley mapping, business
model canvas, skillset engineering, and any future methodology. Each is a
self-contained domain model with its own vocabulary, pipeline, knowledge
base, and presenter.

**Client workspaces** (runtime context): engagement-specific data
produced during execution. Not a bounded context in the DDD sense —
no domain model, no invariants — but a distinct storage context that
sits outside version control.

## The DDD relationship glossary

Evans identifies eight strategic relationships between bounded contexts.
All eight are observable at the Consultamatron integration surface.

| Relationship | Definition | Consultamatron example |
|---|---|---|
| **Shared Kernel** | Two contexts share a common model that both depend on and neither can change unilaterally | `resources/` directory — org-research writes it, every project reads it. Change requires re-agreement. |
| **Published Language** | A context publishes a well-documented, versioned format that others consume | Gate artifact schemas (`.agreed.md`, `.agreed.owm`), entity definitions in `entities.py`, the semantic pack convention |
| **Conformist** | A downstream context accepts the upstream model without translation | Skillsets accept the PipelineStage entity schema as-is. No translation layer, no local model — they populate the practice layer's types directly. |
| **Customer-Supplier** | Upstream context plans with downstream needs in mind; downstream has influence but not control | Practice layer (supplier) designs entity schemas considering skillset needs. Skillset authors (customers) provide feedback. Neither has unilateral control. |
| **Anti-Corruption Layer** | A context insulates itself from an external model through a translation boundary | Per-skillset research skills translate external data (web research, client documents) into the semantic pack format before it enters the domain model |
| **Open Host Service** | A context exposes a general-purpose protocol that any consumer can use without bilateral negotiation | The semantic pack convention — any bounded context can supply packs; the practice layer reads them without per-skillset configuration |
| **Separate Ways** | Two contexts have no integration and operate independently | Skillsets have no inter-dependencies. WM does not import from BMC. Each satisfies the integration surface independently. (Acyclic Dependencies Principle, Martin) |
| **Partnership** | Two contexts succeed or fail together and co-evolve their integration | Operator and agent in the propose-negotiate-agree loop. Neither can produce a gate artifact alone. |

## What the map reveals

### The practice layer is an Open Host Service

The integration surface is not a bilateral negotiation between practice and
each skillset. It is a published protocol that any skillset can satisfy
without the practice layer knowing it exists in advance. This is the Open
Host Service pattern — the practice layer publishes its expectations;
skillsets conform to them.

The Open Host Service manifests through discovery mechanisms: DI scan
finds Protocol implementations, filesystem convention finds knowledge
packs, pack manifests find typed items. No registration is required
beyond satisfying the convention.

### Skillsets are Conformists with influence

Skillsets accept the practice layer's entity schemas (PipelineStage,
ProjectContribution, GateInspector) without translation. They populate
the upstream model directly. This is the Conformist relationship —
the downstream context accepts the upstream model as-is.

But skillset authors have influence. When the pipeline entity does not
serve a methodology's needs, the schema evolves. This is the Customer-
Supplier overlay: the practice layer plans with skillset needs in mind.
The influence channel is the PR process, not a runtime mechanism.

### The Shared Kernel is small and explicit

`resources/` is the only shared kernel between bounded contexts within
an engagement. Org-research writes it; every project reads it. The
immutability invariant (gate protocol) means the kernel does not change
after agreement — the dangerous part of shared kernels (concurrent
mutation) is eliminated by convention.

The practice layer entities (`entities.py`) are a second shared kernel
at the code level — every bounded context depends on them. The Stable
Dependencies Principle (Martin) governs this: entities change rarely and
are the most abstract layer.

### Separate Ways is structural, not accidental

Skillsets do not integrate with each other. This is by design — the
Acyclic Dependencies Principle applied to bounded contexts. If WM
needed BMC data, it would go through the shared kernel (client workspace
resources), not through a direct dependency.

The conformance test for this is `doctrine_no_cross_bc_imports`: the
existing doctrine test suite structurally enforces Separate Ways.

### Anti-Corruption Layers sit at the research boundary

The messiest data enters through research skills. Web research, uploaded
documents, operator-provided context — all of this is unstructured
external data that must not leak into the domain model raw. Per-skillset
research skills (org-research, ns-research) are Anti-Corruption Layers:
they translate external mess into the semantic pack format before it
reaches the bounded context.

The semantic pack convention is what makes the ACL practical — there
is a well-defined target format for the translation.

### Partnership exists at the human-agent boundary

The propose-negotiate-agree loop is a Partnership relationship between
operator and agent. Gate artifacts cannot be produced by either party
alone. The agent proposes, the operator evaluates, agreement is
bilateral. This is the one relationship that does not sit at the
practice/skillset boundary — it sits at the human/machine boundary,
orthogonal to the integration surface.

## How capabilities map to DDD relationships

Each capability at the integration surface instantiates one or more
DDD relationships:

| Capability | Primary relationship | Secondary |
|---|---|---|
| Pipeline declaration | Conformist | Published Language |
| Gate inspection | Published Language | Shared Kernel (gate protocol) |
| Deliverable presentation | Conformist | — |
| Service registration | Open Host Service | — |
| Knowledge packs | Open Host Service | Published Language |
| Knowledge protocols | Customer-Supplier | Published Language |
| Research strategies | Anti-Corruption Layer | Open Host Service |
| Analysis | Customer-Supplier | Open Host Service |
| Pedagogic metadata | Open Host Service | — |
| Iteration evidence | Partnership | — |
| Conformance testing | Customer-Supplier | — |
| Voices | Separate Ways (currently) | — |

## The context map as diagnostic tool

When integration friction arises, the context map diagnoses where:

**Conformist friction**: a skillset needs the upstream model to change.
The Customer-Supplier overlay kicks in — raise a PR, negotiate the
schema evolution. If the practice layer resists change, the Conformist
relationship degrades.

**Shared Kernel friction**: two skillsets need `resources/` in different
formats. The shared kernel is too large. Solution: narrow the kernel,
move format-specific translation into per-skillset ACL code.

**Missing ACL friction**: external data leaks into domain models without
translation. Symptoms: inconsistent formats, model-dependent parsing,
token waste. Solution: add a research skill that translates to the
semantic pack convention.

**Separate Ways violation**: one skillset imports from another.
Symptoms: `doctrine_no_cross_bc_imports` fails. Solution: extract the
shared concept into the practice layer or the shared kernel.

## References

- [The Integration Surface](integration-surface.md) — hexagonal
  architecture perspective on the same boundary
- [Capabilities Pack](capabilities/index.md) — the full catalogue of
  twelve capabilities
- [The Engagement Protocol](engagement-protocol.md) — the three nested
  protocols that the integration surface serves
- [The Semantic Waist](semantic-waist.md) — the typed data layer and
  its DDD vocabulary
- Evans, *Domain-Driven Design* — Chapter 14: Context Map
