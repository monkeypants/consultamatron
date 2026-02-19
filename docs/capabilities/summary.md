# Skillset Capabilities — Summary

The practice layer defines twelve capabilities at the integration boundary.
Each capability is a port: the practice layer specifies the contract and
provides the consuming machinery; the skillset supplies a domain-specific
adapter. A wardley mapping skillset and a business model canvas skillset
both satisfy the same twelve contracts, but the adapters look nothing alike.

## Two mechanisms

**Code ports** are Python Protocol classes in `src/practice/`. The skillset
implements the protocol; the DI container wires it; conformance tests verify
it. Code ports cost zero tokens and fail at import time if violated.
Pipeline declaration, gate inspection, deliverable presentation, and service
registration are code ports. These are the mature capabilities — the ones
with existing tests and runtime enforcement.

**Language ports** are filesystem conventions with documented structural
contracts. The skillset supplies files in agreed formats; skills read them
by convention. Language ports cost tokens to verify and cannot be enforced
by import-time checks. Knowledge packs, knowledge protocols, research
strategies, analysis, and pedagogic metadata are language ports. These are
the emerging capabilities — contracts are documented but enforcement is
partial or absent.

Two capabilities — iteration evidence and voices — have no defined mechanism
yet. They are real integration facets observed in practice but not yet
crystallised into either mechanism.

## Direction

All twelve current capabilities are **driven**: the practice layer reaches
into the skillset and reads what it finds. The reverse direction (skillset
drives practice) exists conceptually — the dyad driving the engagement is
the canonical example — but no driven-outward capability has been formalised.

## Maturity

Capabilities progress from **nascent** (contract documented, no enforcement)
through **established** (structural tests exist, partial coverage) to
**mature** (full structural tests, semantic verification defined). Three
capabilities are mature, three are established, six are nascent. The
maturity gradient tracks the platform's path from documented conventions
to structural enforcement.

## What this pack is for

A skillset contributor reads individual capability files to understand what
adapters their skillset must provide. A skillset engineer reads the
frontmatter as a structured evaluation checklist. A platform developer reads
the pack to understand the integration surface they are maintaining. The
`_bytecode/` summaries let an agent select relevant capabilities without
loading every file.

## Further reading

- [Integration Surface](../integration-surface.md) — what a capability is,
  why they exist, how the protocol composes
- [Context Mapping the Integration Surface](../context-mapping-the-integration-surface.md) —
  DDD analysis of the practice/skillset boundary
- [Language Port Testing](../articles/language-port-testing.md) — verification
  strategy for non-code adapters
- [Capability Token Economics](../articles/capability-token-economics.md) —
  scaling rules for token-burning verification
