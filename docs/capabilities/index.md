---
name: skillset-capabilities
purpose: >
  Catalogue of every integration facet at the practice/skillset boundary.
  Each capability describes a port the practice layer defines and the
  adapter contract a skillset must satisfy to participate.
actor_goals:
  - actor: skillset contributor
    goal: understand what adapters a new skillset must provide
  - actor: skillset engineer (rs-assess)
    goal: evaluate integration quality against capability contracts
  - actor: platform developer
    goal: maintain and extend the Consultamatron Integration Protocol
  - actor: human operator
    goal: understand what the practice layer provides and how skillsets plug in
triggers:
  - building a new skillset from scratch
  - evaluating skillset quality with rs-assess
  - adding a new capability to the integration protocol
  - debugging integration failures between practice layer and skillsets
  - reviewing PRs that modify skillset adapters
---

# Skillset Capabilities

The Consultamatron Integration Protocol defines the boundary between the
practice layer (domain-agnostic platform) and skillset bounded contexts
(domain-specific methodology). Each capability in this pack describes one
facet of that boundary.

## Routing

Agents: read `_bytecode/` summaries to select relevant capabilities.
Humans: read `summary.md` for a prose synthesis, or browse capability
files directly.

## Structure

Each capability file has YAML frontmatter matching the
`practice.entities.Capability` entity. The frontmatter is the structured
contract (how to use). The prose body is pedagogic (how to understand).

## Items

- `pipeline-declaration.md` — skillsets declare pipeline stages for engagement orchestration
- `gate-inspection.md` — practice layer derives state from gate artifacts
- `deliverable-presentation.md` — skillsets assemble workspace artifacts into deliverable content
- `service-registration.md` — skillsets register domain-specific services on the DI container
- `knowledge-packs.md` — skillsets supply dual-audience knowledge through the semantic pack convention
- `knowledge-protocols.md` — use cases consume typed knowledge items structurally
- `research-strategies.md` — skillsets supply domain-specific research strategy descriptions
- `analysis.md` — skillsets supply luminaries and domain vocabulary for multi-perspective synthesis
- `pedagogic-metadata.md` — skillsets supply concept catalogues and learning sequences
- `iteration-evidence.md` — review findings feed domain-specific improvement pipelines
- `conformance-testing.md` — skillsets supply testing helpers for structural verification
- `voices.md` — skillsets supply voice profiles for operator pedagogy repackaging
