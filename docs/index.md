---
name: platform-knowledge
purpose: >
  Design rationale, conventions, and operating procedures for the
  Consultamatron platform. The primary knowledge base for agents and
  contributors working on or with the practice layer.
actor_goals:
  - actor: agent
    goal: understand platform conventions before modifying code
  - actor: contributor
    goal: learn design rationale and architectural decisions
  - actor: operator
    goal: understand how the platform works and why
triggers:
  - starting a new agent session
  - modifying platform infrastructure
  - adding or modifying a knowledge pack
  - debugging conformance test failures
---

# Platform Knowledge

Design rationale, conventions, and operating procedures for
Consultamatron.

## Routing

Agents: read `_bytecode/` summaries to select relevant items.
Humans: browse item files directly.

## Items

- `context-mapping-the-integration-surface.md` — DDD context mapping applied to the practice/skillset boundary
- `deliverable-architecture.md` — how skillsets assemble workspace artifacts into deliverables
- `engagement-protocol.md` — lifecycle of a consulting engagement
- `howto-pack-and-wrap.md` — procedure for compiling knowledge pack bytecode
- `integration-surface.md` — the practice/skillset integration boundary
- `knowledge-protocols.md` — typed knowledge consumption patterns
- `open-standards.md` — external standards the platform builds on
- `prompt-engineering.md` — prompt design conventions for skills
- `semantic-packs.md` — the knowledge pack convention
- `semantic-waist.md` — the narrow typed layer between practice and skillsets
- `wetware-efficiency.md` — human cognitive efficiency in agent-assisted work

## Composite items

- `capabilities/` — catalogue of integration facets at the practice/skillset boundary
