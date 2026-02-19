---
type: capability
name: deliverable-presentation
description: >
  Practice renders deliverable sites from structured content. Each
  skillset implements a ProjectPresenter that assembles its workspace
  artifacts into ProjectContribution entities the renderer consumes.
direction: driven
mechanism: code_port
adapter_contract: >
  A PRESENTER_FACTORY tuple in __init__.py mapping skillset name to a
  factory function (workspace_root, repo_root) -> ProjectPresenter.
  The presenter's present() method returns a ProjectContribution
  containing ContentPage groups, NarrativeGroup tours, and Figure
  elements assembled from the skillset's workspace artifacts.
discovery: di_scan
maturity: mature
hidden_decision: >
  How a skillset's workspace artifacts are structured and how they
  assemble into presentable content. A wardley map project has OWM
  files, atlas analyses, and narrative tours. A BMC project has canvas
  blocks and segment documents. The practice layer sees only
  ProjectContribution entities.
information_expert: >
  The skillset's presenter implementation. It knows the workspace
  artifact layout, the assembly logic, and the content types that the
  skillset produces. The renderer knows nothing about these.
structural_tests:
  - doctrine_presenter_returns_contribution
semantic_verification: null
---

# Deliverable Presentation

Deliverable presentation is the output pipeline. The practice layer
renders deliverable sites; the skillset knows how to assemble its own
artifacts into structured content.

## What the practice layer provides

The `ProjectPresenter` protocol:

```python
class ProjectPresenter(Protocol):
    def present(self, project: Project,
                research_topics: list[ResearchTopic]) -> ProjectContribution: ...
```

And the `SiteRenderer` protocol that consumes `ProjectContribution`
entities to produce static HTML. The data flowing between them is
defined in `src/practice/content.py`: `ContentPage`, `PageGroup`,
`NarrativeStop`, `NarrativeGroup`, `Figure`, `ProjectContribution`.

Adding a new skillset requires: declare `SKILLSETS`, implement a
presenter, register via `PRESENTER_FACTORY`. No changes to renderer,
use case, or protocol. This is OCP applied to the deliverable pipeline.

## What the skillset supplies

A `PRESENTER_FACTORY` attribute in the BC's `__init__.py` — a tuple of
`(skillset_name, factory_function)`. The factory constructs the
presenter with access to the workspace root and repository root.

The presenter reads workspace artifacts (OWM files, markdown documents,
tour manifests, atlas analyses) and assembles them into the Published
Language of `ProjectContribution`. This assembly is the
Anti-Corruption Layer (Evans) — it translates skillset-specific
workspace formats into the generic content model.

## Emerging sibling: presentation preparation

This capability currently covers artifact assembly for the deliverable
site. A related but distinct capability is emerging: preparing
analytical content for operator consumption with pedagogic intent. This
would supply metadata about what concepts the operator encounters, what
learning sequences they imply, and what pedagogic affordances the
content provides.

When the pedagogic preparation dimension stabilises, this capability
splits into two: deliverable assembly (the existing code port) and
presentation preparation (a language port supplying pedagogic metadata).

## References

- [Deliverable Architecture](../deliverable-architecture.md) —
  presenter plugins, renderer protocol, content entities
- [Engagement Protocol](../articles/engagement-protocol.md) §11 —
  the contributor contract
